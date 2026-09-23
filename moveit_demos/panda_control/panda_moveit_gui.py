#!/usr/bin/python3
"""Panda MoveIt Tkinter 控制面板（程序化拖关节 / 末端位姿）。

整体结构
--------
1. PandaGuiNode
   - 继承 panda_moveit_demo.PandaMoveItDemo（内部走 /move_action）
   - 订阅 /joint_states，读当前 7 轴
   - 用 TF 查 panda_link0 → panda_link8，得到末端 xyz + rpy

2. SliderRow
   - 一行：标签 + 滑条 + 数值框 + 单位

3. PandaTkApp
   - 左侧 J1–J7（度），右侧 X/Y/Z（米）与 Rx/Ry/Rz（度）
   - Speed：同时作为 MoveIt 速度/加速度缩放系数
   - 按钮：同步状态、按关节/位姿规划执行、Ready/Extended、夹爪

4. main()
   - 后台线程 spin ROS；主线程跑 Tk
   - 规划执行放子线程，避免界面卡死（滑条数值在主线程先读好）

依赖与启动
----------
先开仿真：
  ros2 launch moveit_resources_panda_moveit_config demo.launch.py
再开本面板：
  bash run_panda_moveit_gui.sh

限位说明
--------
- JOINT_LIMITS_RAD：来自 URDF safety_controller 软限位（弧度）
- CART_LIMITS：GUI 经验工作空间，不是官方笛卡尔硬限位
"""

from __future__ import annotations

import math
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk
from typing import Dict, List, Optional, Tuple

import rclpy
from geometry_msgs.msg import Pose, Quaternion
from rclpy.executors import SingleThreadedExecutor
from sensor_msgs.msg import JointState
from tf2_ros import Buffer, TransformListener
from tf_transformations import euler_from_quaternion, quaternion_from_euler

from panda_moveit_demo import JOINT_NAMES, NAMED_JOINT_STATES, PandaMoveItDemo

# ---------------------------------------------------------------------------
# 限位常量
# ---------------------------------------------------------------------------
# 软限位（弧度）：moveit_resources_panda_description/urdf/panda.urdf
# 中各关节 safety_controller 的 soft_lower_limit / soft_upper_limit
JOINT_LIMITS_RAD: List[Tuple[float, float]] = [
    (-2.8973, 2.8973),   # J1
    (-1.7628, 1.7628),   # J2
    (-2.8973, 2.8973),   # J3
    (-3.0718, -0.0698),  # J4
    (-2.8973, 2.8973),   # J5
    (-0.0175, 3.7525),   # J6
    (-2.8973, 2.8973),   # J7
]

# 末端滑条范围（相对 panda_link0）：经验工作空间，仅限制 GUI 拖动范围
CART_LIMITS = {
    "x": (0.15, 0.70),       # 米
    "y": (-0.45, 0.45),
    "z": (0.05, 0.80),
    "rx": (-180.0, 180.0),   # 度（欧拉角）
    "ry": (-180.0, 180.0),
    "rz": (-180.0, 180.0),
}


class PandaGuiNode(PandaMoveItDemo):
    """ROS 侧：关节状态 + 末端 TF；运动接口复用父类 MoveGroup 封装。"""

    def __init__(self) -> None:
        super().__init__(node_name="panda_moveit_gui")
        self._lock = threading.Lock()
        self._joint_positions: Dict[str, float] = {name: 0.0 for name in JOINT_NAMES}
        self.create_subscription(JointState, "/joint_states", self._on_joint_state, 10)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def _on_joint_state(self, msg: JointState) -> None:
        with self._lock:
            for name, pos in zip(msg.name, msg.position):
                if name in self._joint_positions:
                    self._joint_positions[name] = float(pos)

    def current_joints(self) -> List[float]:
        """当前 7 轴关节角（弧度），顺序同 JOINT_NAMES。"""
        with self._lock:
            return [self._joint_positions[name] for name in JOINT_NAMES]

    def current_ee_pose(self) -> Optional[Tuple[float, float, float, float, float, float]]:
        """末端位姿 (x,y,z,rx,ry,rz)：位置米、姿态度，相对 panda_link0。"""
        try:
            tf = self.tf_buffer.lookup_transform(
                "panda_link0",
                "panda_link8",
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.2),
            )
        except Exception:
            return None
        t = tf.transform.translation
        q = tf.transform.rotation
        rx, ry, rz = euler_from_quaternion([q.x, q.y, q.z, q.w])
        return (
            float(t.x),
            float(t.y),
            float(t.z),
            math.degrees(rx),
            math.degrees(ry),
            math.degrees(rz),
        )


class SliderRow:
    """单行控件：标签 | 滑条 | 可编辑数值 | 单位。"""

    def __init__(
        self,
        parent,
        label: str,
        low: float,
        high: float,
        resolution: float,
        unit: str,
        initial: float = 0.0,
    ) -> None:
        self.var = tk.DoubleVar(value=initial)
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)
        ttk.Label(frame, text=label, width=8).pack(side="left")
        self.scale = ttk.Scale(
            frame,
            from_=low,
            to=high,
            orient="horizontal",
            variable=self.var,
            command=lambda _v: self._sync_entry(),
        )
        self.scale.pack(side="left", fill="x", expand=True, padx=4)
        self.entry = ttk.Entry(frame, width=8)
        self.entry.pack(side="left")
        self.entry.insert(0, f"{initial:.3f}")
        self.entry.bind("<Return>", self._on_entry)
        self.entry.bind("<FocusOut>", self._on_entry)
        ttk.Label(frame, text=unit, width=4).pack(side="left")
        self.low = low
        self.high = high
        self.resolution = resolution

    def _sync_entry(self) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, f"{self.var.get():.3f}")

    def _on_entry(self, _event=None) -> None:
        try:
            value = float(self.entry.get())
        except ValueError:
            self._sync_entry()
            return
        value = min(max(value, self.low), self.high)
        self.var.set(value)
        self._sync_entry()

    def get(self) -> float:
        return float(self.var.get())

    def set(self, value: float) -> None:
        value = min(max(float(value), self.low), self.high)
        self.var.set(value)
        self._sync_entry()


class PandaTkApp:
    """Tk 界面：读滑条 → 调 MoveIt → 在 RViz 仿真里看结果。"""

    def __init__(self, node: PandaGuiNode) -> None:
        self.node = node
        self.busy = False  # 防止连点导致多次规划并行
        self.root = tk.Tk()
        self.root.title("Panda MoveIt 控制面板")
        self.root.geometry("920x720")
        self.root.minsize(820, 640)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        family = self._cjk_family()
        self.root.option_add("*Font", tkfont.Font(family=family, size=10))

        self.status = tk.StringVar(value="已连接 move_group。可调节滑条后点击执行。")
        self._build()
        self.root.after(200, self._poll_status)
        # 启动后自动同步一次当前状态
        self.root.after(600, self.sync_from_robot)

    def _cjk_family(self) -> str:
        families = set(tkfont.families(self.root))
        for name in ("Noto Sans CJK SC", "Noto Sans CJK JP", "Droid Sans Fallback", "WenQuanYi Micro Hei"):
            if name in families:
                return name
        return "Sans"

    def _build(self) -> None:
        """搭建左右栏滑条与底部速度、按钮、状态栏。"""
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="both", expand=True)
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)

        left = ttk.LabelFrame(top, text="关节角（度）", padding=8)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        right = ttk.LabelFrame(top, text="末端位姿（相对 panda_link0）", padding=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.joint_sliders: List[SliderRow] = []
        for i, (low, high) in enumerate(JOINT_LIMITS_RAD):
            row = SliderRow(
                left,
                f"J{i + 1}",
                math.degrees(low),
                math.degrees(high),
                0.1,
                "°",
                0.0,
            )
            self.joint_sliders.append(row)

        self.cart_sliders: Dict[str, SliderRow] = {}
        for key, unit, default in (
            ("x", "m", 0.35),
            ("y", "m", 0.0),
            ("z", "m", 0.45),
            ("rx", "°", 180.0),
            ("ry", "°", 0.0),
            ("rz", "°", 45.0),
        ):
            low, high = CART_LIMITS[key]
            self.cart_sliders[key] = SliderRow(right, key.upper(), low, high, 0.001, unit, default)

        bottom = ttk.Frame(self.root, padding=8)
        bottom.pack(fill="x")

        speed_frame = ttk.LabelFrame(bottom, text="速度", padding=8)
        speed_frame.pack(fill="x", pady=(0, 8))
        self.speed = SliderRow(speed_frame, "Speed", 0.05, 1.0, 0.01, "×", 0.25)
        ttk.Label(
            speed_frame,
            text="同时作为 MoveIt 的 max_velocity_scaling_factor 与 max_acceleration_scaling_factor",
            foreground="#555555",
        ).pack(anchor="w")

        btns = ttk.Frame(bottom)
        btns.pack(fill="x", pady=(0, 8))
        ttk.Button(btns, text="从机器人同步", command=self.sync_from_robot).pack(side="left", padx=3)
        ttk.Button(btns, text="执行关节运动", command=self.execute_joints).pack(side="left", padx=3)
        ttk.Button(btns, text="执行位姿运动", command=self.execute_pose).pack(side="left", padx=3)
        ttk.Button(btns, text="Ready", command=lambda: self.goto_named("ready")).pack(side="left", padx=3)
        ttk.Button(btns, text="Extended", command=lambda: self.goto_named("extended")).pack(side="left", padx=3)
        ttk.Button(btns, text="开夹爪", command=lambda: self._run_async("开夹爪", lambda: self.node.set_gripper(0.035))).pack(side="left", padx=3)
        ttk.Button(btns, text="关夹爪", command=lambda: self._run_async("关夹爪", lambda: self.node.set_gripper(0.0))).pack(side="left", padx=3)

        ttk.Label(bottom, textvariable=self.status, wraplength=880).pack(fill="x")

    def _speed(self) -> float:
        return max(0.05, min(1.0, self.speed.get()))

    def sync_from_robot(self) -> None:
        """把当前关节角、末端位姿写回滑条。"""
        joints = self.node.current_joints()
        for slider, value in zip(self.joint_sliders, joints):
            slider.set(math.degrees(value))
        pose = self.node.current_ee_pose()
        if pose is None:
            self.status.set("已同步关节；末端 TF 暂不可用，稍后再点同步。")
            return
        x, y, z, rx, ry, rz = pose
        self.cart_sliders["x"].set(x)
        self.cart_sliders["y"].set(y)
        self.cart_sliders["z"].set(z)
        self.cart_sliders["rx"].set(rx)
        self.cart_sliders["ry"].set(ry)
        self.cart_sliders["rz"].set(rz)
        self.status.set(
            f"已同步  J=[{', '.join(f'{math.degrees(v):.1f}' for v in joints)}]°  "
            f"xyz=({x:.3f},{y:.3f},{z:.3f})  rpy=({rx:.1f},{ry:.1f},{rz:.1f})°"
        )

    def execute_joints(self) -> None:
        """按左侧 7 轴目标做 MoveIt 关节空间规划并执行。"""
        # 必须在主线程读 Tk 变量，再交给后台线程
        positions = [math.radians(s.get()) for s in self.joint_sliders]
        speed = self._speed()

        def work() -> bool:
            return self.node.move_to_joint_positions(
                positions,
                velocity_scale=speed,
                accel_scale=speed,
                label="gui_joint",
            )

        self._run_async("关节运动", work)

    def execute_pose(self) -> None:
        """按右侧 xyz + rpy 目标做 MoveIt 笛卡尔位姿规划并执行。"""
        x = self.cart_sliders["x"].get()
        y = self.cart_sliders["y"].get()
        z = self.cart_sliders["z"].get()
        rx = math.radians(self.cart_sliders["rx"].get())
        ry = math.radians(self.cart_sliders["ry"].get())
        rz = math.radians(self.cart_sliders["rz"].get())
        qx, qy, qz, qw = quaternion_from_euler(rx, ry, rz)
        pose = Pose()
        pose.position.x = x
        pose.position.y = y
        pose.position.z = z
        pose.orientation = Quaternion(x=qx, y=qy, z=qz, w=qw)
        speed = self._speed()

        def work() -> bool:
            return self.node.move_to_pose(
                pose,
                velocity_scale=speed,
                accel_scale=speed,
                label="gui_pose",
            )

        self._run_async("位姿运动", work)

    def goto_named(self, name: str) -> None:
        """跳到 SRDF 命名位姿（ready / extended 等）。"""
        speed = self._speed()
        positions = list(NAMED_JOINT_STATES[name])

        def work() -> bool:
            ok = self.node.move_to_joint_positions(
                positions,
                velocity_scale=speed,
                accel_scale=speed,
                label=name,
            )
            if ok:
                self.root.after(0, self.sync_from_robot)
            return ok

        self._run_async(f"命名位姿 {name}", work)

    def _run_async(self, title: str, func) -> None:
        """后台执行规划，结束后回主线程更新状态栏。"""
        if self.busy:
            messagebox.showinfo("忙", "上一次运动还在执行，请稍候。")
            return
        self.busy = True
        self.status.set(f"正在执行：{title} …")

        def runner() -> None:
            try:
                ok = func()
                msg = f"{title}：{'成功' if ok else '失败（看终端日志）'}"
            except Exception as exc:
                ok = False
                msg = f"{title}：异常 {exc}"

            def done() -> None:
                self.busy = False
                self.status.set(msg)
                if ok and title in ("关节运动", "位姿运动"):
                    self.sync_from_robot()

            self.root.after(0, done)

        threading.Thread(target=runner, daemon=True).start()

    def _poll_status(self) -> None:
        # 占位定时器，保持 Tk 事件循环；不自动改滑条，以免拖动时被覆盖
        if self.root.winfo_exists():
            self.root.after(300, self._poll_status)

    def close(self) -> None:
        self.root.quit()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    """ROS 后台 spin + Tk 前台界面。"""
    rclpy.init()
    node = PandaGuiNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    spin_thread = threading.Thread(target=executor.spin, daemon=True)
    spin_thread.start()
    app = PandaTkApp(node)
    try:
        app.run()
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
