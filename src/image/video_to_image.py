import cv2
import numpy as np
import os


def extract_frames(video_path, num_frames=10):
    video_cap = cv2.VideoCapture(video_path)
    if not video_cap.isOpened():
        raise ValueError(f"Error opening video file {video_path}")
    total_frames = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = set(
        [int(i) for i in np.linspace(0, total_frames - 1, num=num_frames)]
    )
    extracted_frames = []
    frame_idx = 0
    while True:
        success, frame = video_cap.read()
        if not success:
            break
        if frame_idx in frame_indices:
            extracted_frames.append(frame)
            frame_indices.remove(frame_idx)
            if not frame_indices:
                break
        frame_idx += 1
    video_cap.release()
    return extracted_frames


def save_frames(extracted_frames, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    res = []
    for i, frame in enumerate(extracted_frames):
        filename = os.path.join(output_dir, f"frame_{i}.jpg")
        if os.path.exists(filename):
            os.remove(filename)
        cv2.imwrite(filename, frame)
        res.append(filename)
    return res


if __name__ == '__main__':
    video_path = "D:\\Projects\\media-empire\\tmp\\2023-03-10T15-25-33_slide_in_top_all.mp4"
    frames = extract_frames(video_path, num_frames=10)

    save_frames(frames, "D:\\Projects\\media-empire\\tmp\\")
    print(frames)
