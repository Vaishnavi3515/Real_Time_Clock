"""
Harry Potter–style invisibility cloak (OpenCV + NumPy)

Fully automatic — no menus:
  1. Captures a clean background on startup (step out of view).
  2. Live camera: detects the bright red cloth and replaces ONLY
     those pixels with the stored background. Everything else
     (your face, body, walls, furniture) stays fully visible.

Key controls over earlier versions:
  - Strict, non-skin red range (rejects your face)
  - Largest-connected-blob selection (only the single biggest red
    region gets cloaked — kills stray specks in the background)
  - Area threshold (must be larger than 0.5% of the frame)
  - Optional fallback: if you bring the cloth RIGHT UP to the
    camera, the very large blob also passes the threshold
  - Morphological cleanup + soft edge blend

Keys (while running):
  r = recapture background
  s = save snapshot
  m = toggle mask debug window
  q = quit
"""

import cv2
import numpy as np
import time
import os
import sys


# ─────────────────────────────────────────────────────────────────────
# 1. Background capture
# ─────────────────────────────────────────────────────────────────────
def capture_background(cap, seconds=3):
    """Median over N frames = a clean static background."""
    print(f"[bg] Step OUT of frame. Capturing background for {seconds}s...")
    frames = []
    end = time.time() + seconds
    while time.time() < end:
        ok, frame = cap.read()
        if not ok:
            continue
        frame = cv2.flip(frame, 1)  # mirror so stored bg matches live view
        frames.append(frame)

        remaining = int(end - time.time())
        cv2.putText(frame, f"Stand OUT of frame... {remaining}s",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 0, 255), 2)
        cv2.imshow("Invisibility Cloak", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            sys.exit(0)

    if not frames:
        raise RuntimeError("Could not capture background frames.")
    print(f"[bg] Captured {len(frames)} frames. Building background...")
    return np.median(np.array(frames), axis=0).astype(np.uint8)


# ─────────────────────────────────────────────────────────────────────
# 2. Red detection — STRICT, rejects skin
# ─────────────────────────────────────────────────────────────────────
# Skin tones in HSV sit around hue 0-25 with MEDIUM saturation
# (people are rarely fully saturated) and moderate-to-high value.
# A bright red cloth is hue 0-10 OR 170-180, with HIGH saturation
# and any value. The trick: require saturation >= 100 (skin rarely
# hits that) and require a single large connected blob.

# Strict red range — saturation floor is what rejects skin.
LOWER1 = np.array([0,   110, 80])
UPPER1 = np.array([8,   255, 255])
LOWER2 = np.array([172, 110, 80])
UPPER2 = np.array([180, 255, 255])

# Anything with a hue in 9..171 at the same saturation is NOT red —
# we use this to explicitly exclude anything that could be confused
# with warm skin, brown wood, etc. (We do this in the mask-building
# step below.)


# ─────────────────────────────────────────────────────────────────────
# 3. Mask construction — only the LARGEST connected red blob survives
# ─────────────────────────────────────────────────────────────────────
def build_cloak_mask(hsv, frame_area, prev_mask=None):
    """Return a soft mask of ONLY the cloth.

    Strategy:
      a) Strict red range (skin rejected by saturation floor)
      b) Keep only the LARGEST connected component
         (kills specks in the background, kills dots on the face)
      c) Discard if the largest blob is too small
         (below 0.5% of the frame area = not a cloth)
      d) Morphology + blur
      e) Temporal smoothing: union with previous frame's mask so the
         cloth stays cloaked across frames even if the detection
         flickers slightly
    """
    # a) Strict red detection
    m = (cv2.inRange(hsv, LOWER1, UPPER1) |
         cv2.inRange(hsv, LOWER2, UPPER2))

    # b) Connected components — keep only the largest
    # cv2.connectedComponentsWithStats is in cv2 4.0+
    num, labels, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if num <= 1:
        return np.zeros_like(m)  # no red pixels at all

    # Find the largest non-background component
    # label 0 is the background; skip it
    areas = stats[1:, cv2.CC_STAT_AREA]
    if len(areas) == 0 or areas.max() < frame_area * 0.005:
        # Largest blob is too small to be a cloth
        return np.zeros_like(m)

    largest_label = 1 + int(np.argmax(areas))
    m = (labels == largest_label).astype(np.uint8) * 255

    # d) Morphology + soft blur
    kernel = np.ones((3, 3), np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN,  kernel, iterations=2)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, kernel, iterations=1)
    m = cv2.GaussianBlur(m, (7, 7), 0)

    # e) Temporal smoothing — union with previous frame's mask so the
    # cloak stays solid across frames (prevents flicker holes).
    if prev_mask is not None:
        m = cv2.bitwise_or(m, prev_mask)
        # Slight extra blur to smooth the union
        m = cv2.GaussianBlur(m, (5, 5), 0)

    return m


# ─────────────────────────────────────────────────────────────────────
# 4. Composite
# ─────────────────────────────────────────────────────────────────────
def apply_cloak(frame, background, mask):
    """Where mask is bright, show background; otherwise show frame."""
    alpha = mask.astype(np.float32) / 255.0
    alpha_3 = cv2.merge([alpha, alpha, alpha])
    out = (frame.astype(np.float32)      * (1 - alpha_3) +
           background.astype(np.float32) *      alpha_3)
    return out.astype(np.uint8)


# ─────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[err] Could not open the camera. Check permissions / index.")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Grab a clean background — make sure to step out of frame!
    background = capture_background(cap, seconds=3)
    print("[ok] Background locked. Step in WITH the cloth.")

    snapshot_dir = os.path.join(os.path.dirname(__file__), "snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)
    show_mask = False
    prev_mask = None
    frame_area = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) *
                     cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ok, frame = cap.read()
        if not ok:
            print("[err] Frame read failed.")
            break

        frame = cv2.flip(frame, 1)            # mirror view
        hsv   = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask  = build_cloak_mask(hsv, frame_area, prev_mask=prev_mask)
        prev_mask = mask  # carry forward for temporal smoothing

        output = apply_cloak(frame, background, mask)

        cv2.putText(output, "r=reset bg   s=save   m=mask   q=quit",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255), 2)
        cv2.imshow("Invisibility Cloak", output)

        if show_mask:
            cv2.imshow("Cloak mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            background = capture_background(cap, seconds=3)
        elif key == ord('m'):
            show_mask = not show_mask
            if not show_mask:
                cv2.destroyWindow("Cloak mask")
        elif key == ord('s'):
            ts = time.strftime("%Y%m%d-%H%M%S")
            path = os.path.join(snapshot_dir, f"cloak_{ts}.png")
            cv2.imwrite(path, output)
            print(f"[ok] Saved {path}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
