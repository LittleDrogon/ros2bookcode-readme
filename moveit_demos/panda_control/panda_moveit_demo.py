#!/usr/bin/python3
"""用 MoveIt MoveGroup 动作接口控制已启动的 Panda 仿真。

请先在另一个终端运行：
  ros2 launch moveit_resources_panda_moveit_config demo.launch.py

本脚本会依次：
1. 规划并执行到命名关节位姿 ready / extended
2. 规划并执行一个末端位姿目标
3. 开合夹爪
4. 回到 ready
"""

from __future__ import annotations

import math
import sys
import time
from typing import Dict, List, Optional, Sequence

import rclpy
from control_msgs.action import GripperCommand
from geometry_msgs.msg import Point, Pose, Quaternion
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints,
    JointConstraint,
    MotionPlanRequest,
    OrientationConstraint,
    PositionConstraint,
)
from rclpy.action import ActionClient
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive


JOINT_NAMES = [
    "panda_joint1",
    "panda_joint2",
    "panda_joint3",
    "panda_joint4",
    "panda_joint5",
    "panda_joint6",
    "panda_joint7",
]

# 与 panda.srdf 中 group_state 一致
NAMED_JOINT_STATES: Dict[str, List[float]] = {
    "ready": [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785],
    "extended": [0.0, 0.0, 0.0, 0.0, 0.0, 1.571, 0.785],
    "transport": [0.0, -0.5599, 0.0, -2.97, 0.0, 0.0, 0.785],
}


class PandaMoveItDemo(Node):
    def __init__(self, node_name: str = "panda_moveit_demo") -> None:
        super().__init__(node_name)
        self.move_client = ActionClient(self, MoveGroup, "move_action")
        self.gripper_client = ActionClient(
            self, GripperCommand, "panda_hand_controller/gripper_cmd"
        )
        self.get_logger().info("等待 /move_action …")
        if not self.move_client.wait_for_server(timeout_sec=20.0):
            raise RuntimeError(
                "找不到 /move_action。请先启动:\n"
                "  ros2 launch moveit_resources_panda_moveit_config demo.launch.py"
            )
        self.get_logger().info("已连接 move_group")
        if self.gripper_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().info("已连接夹爪控制器")
            self.has_gripper = True
        else:
            self.get_logger().warning("未找到夹爪动作，将跳过开合夹爪")
            self.has_gripper = False

    def move_to_joint_positions(
        self,
        positions: Sequence[float],
        *,
        group: str = "panda_arm",
        velocity_scale: float = 0.25,
        accel_scale: float = 0.25,
        label: str = "joint goal",
    ) -> bool:
        if len(positions) != len(JOINT_NAMES):
            raise ValueError("关节数量与 JOINT_NAMES 不一致")

        constraints = Constraints()
        constraints.name = label
        for name, value in zip(JOINT_NAMES, positions):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = float(value)
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)
        return self._send_move_goal(
            group=group,
            goal_constraints=[constraints],
            velocity_scale=velocity_scale,
            accel_scale=accel_scale,
            label=label,
        )

    def move_to_named_state(self, name: str) -> bool:
        if name not in NAMED_JOINT_STATES:
            raise KeyError(f"未知命名位姿: {name}，可选: {list(NAMED_JOINT_STATES)}")
        self.get_logger().info(f"前往命名位姿: {name}")
        return self.move_to_joint_positions(NAMED_JOINT_STATES[name], label=name)

    def move_to_pose(
        self,
        pose: Pose,
        *,
        frame_id: str = "panda_link0",
        ee_link: str = "panda_link8",
        group: str = "panda_arm",
        position_tol: float = 0.01,
        orientation_tol: float = 0.05,
        velocity_scale: float = 0.2,
        accel_scale: float = 0.2,
        label: str = "pose goal",
    ) -> bool:
        constraints = Constraints()
        constraints.name = label

        pc = PositionConstraint()
        pc.header.frame_id = frame_id
        pc.link_name = ee_link
        pc.weight = 1.0
        sphere = SolidPrimitive()
        sphere.type = SolidPrimitive.SPHERE
        sphere.dimensions = [position_tol]
        pc.constraint_region.primitives.append(sphere)
        pc.constraint_region.primitive_poses.append(pose)
        constraints.position_constraints.append(pc)

        oc = OrientationConstraint()
        oc.header.frame_id = frame_id
        oc.link_name = ee_link
        oc.orientation = pose.orientation
        oc.absolute_x_axis_tolerance = orientation_tol
        oc.absolute_y_axis_tolerance = orientation_tol
        oc.absolute_z_axis_tolerance = orientation_tol
        oc.weight = 1.0
        constraints.orientation_constraints.append(oc)

        self.get_logger().info(
            f"前往位姿: xyz=({pose.position.x:.3f}, {pose.position.y:.3f}, {pose.position.z:.3f})"
        )
        return self._send_move_goal(
            group=group,
            goal_constraints=[constraints],
            velocity_scale=velocity_scale,
            accel_scale=accel_scale,
            label=label,
        )

    def set_gripper(self, position: float, max_effort: float = 20.0) -> bool:
        if not self.has_gripper:
            return False
        goal = GripperCommand.Goal()
        goal.command.position = float(position)
        goal.command.max_effort = float(max_effort)
        self.get_logger().info(f"夹爪目标开合: {position:.3f} m")
        future = self.gripper_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        goal_handle = future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error("夹爪目标被拒绝")
            return False
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=20.0)
        result = result_future.result()
        ok = result is not None and result.result.reached_goal
        self.get_logger().info(f"夹爪结果: {'成功' if ok else '未完全到位/超时'}")
        return bool(ok)

    def _send_move_goal(
        self,
        *,
        group: str,
        goal_constraints: List[Constraints],
        velocity_scale: float,
        accel_scale: float,
        label: str,
        planning_time: float = 8.0,
    ) -> bool:
        request = MotionPlanRequest()
        request.group_name = group
        request.num_planning_attempts = 8
        request.allowed_planning_time = planning_time
        request.max_velocity_scaling_factor = velocity_scale
        request.max_acceleration_scaling_factor = accel_scale
        request.start_state.is_diff = True
        request.goal_constraints = goal_constraints
        # 留空则使用 move_group 默认 OMPL 规划器
        request.pipeline_id = "ompl"

        goal = MoveGroup.Goal()
        goal.request = request
        goal.planning_options.plan_only = False
        goal.planning_options.look_around = False
        goal.planning_options.replan = True
        goal.planning_options.replan_attempts = 3
        goal.planning_options.replan_delay = 0.5

        self.get_logger().info(f"规划并执行: {label}")
        send_future = self.move_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=15.0)
        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error(f"MoveGroup 目标被拒绝: {label}")
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=90.0)
        wrapped = result_future.result()
        if wrapped is None:
            self.get_logger().error(f"未收到 MoveGroup 结果: {label}")
            return False

        result = wrapped.result
        error_code = result.error_code.val
        # moveit_msgs/MoveItErrorCodes SUCCESS = 1
        if error_code == 1:
            self.get_logger().info(f"完成: {label}")
            return True
        self.get_logger().error(f"失败: {label}  error_code={error_code}")
        return False


def make_pose(x: float, y: float, z: float, yaw: float = 0.0) -> Pose:
    """末端朝下的可达位姿（相对 panda_link0）。"""
    pose = Pose()
    pose.position = Point(x=x, y=y, z=z)
    # 先绕 X 转 180°（朝下），再绕 Z 转 yaw
    half = yaw * 0.5
    # q_down = (1, 0, 0, 0); q_yaw = (0, 0, sin, cos)
    # q = q_yaw * q_down
    pose.orientation = Quaternion(
        x=math.cos(half),
        y=math.sin(half),
        z=0.0,
        w=0.0,
    )
    return pose


def main() -> int:
    rclpy.init()
    node: Optional[PandaMoveItDemo] = None
    try:
        node = PandaMoveItDemo()
        steps = [
            ("ready", lambda: node.move_to_named_state("ready")),
            ("extended", lambda: node.move_to_named_state("extended")),
            (
                "pose_a",
                lambda: node.move_to_pose(make_pose(0.35, -0.20, 0.45)),
            ),
            (
                "pose_b",
                lambda: node.move_to_pose(make_pose(0.40, 0.20, 0.40)),
            ),
            ("gripper_open", lambda: node.set_gripper(0.035) or True),
            ("gripper_close", lambda: node.set_gripper(0.0) or True),
            ("back_ready", lambda: node.move_to_named_state("ready")),
        ]

        for name, action in steps:
            node.get_logger().info(f"==== 步骤: {name} ====")
            ok = action()
            if not ok and name not in ("gripper_open", "gripper_close"):
                node.get_logger().error(f"步骤失败，提前结束: {name}")
                return 1
            time.sleep(0.5)

        node.get_logger().info("Demo 全部完成。可在 RViz 中观察机械臂运动。")
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"[panda_moveit_demo] {exc}", file=sys.stderr)
        return 1
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
