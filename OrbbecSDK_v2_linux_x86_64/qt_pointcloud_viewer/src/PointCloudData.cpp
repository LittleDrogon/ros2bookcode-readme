#include "PointCloudData.h"

void PointCloudData::clear() {
    std::lock_guard<std::mutex> lock(mutex_);
    points_.clear();
}

void PointCloudData::setPoints(std::vector<Point> &&points) {
    std::lock_guard<std::mutex> lock(mutex_);
    points_ = std::move(points);
}

std::vector<PointCloudData::Point> PointCloudData::snapshot() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return points_;
}

size_t PointCloudData::size() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return points_.size();
}
