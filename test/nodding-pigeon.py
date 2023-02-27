from noddingpigeon.inference import predict_video
from noddingpigeon.video import VideoSegment  # Optional.

t = predict_video(
  # "no.mp4",
  None,
  video_segment=VideoSegment.LAST,  # Optionally change these parameters.
  motion_threshold=0.5,
  gesture_threshold=0.9
)