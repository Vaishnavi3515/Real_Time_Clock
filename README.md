<div align="center">

# 🪄 Real-Time Invisibility Cloak

### Make a red cloth disappear in real time using Computer Vision.

A Harry Potter–inspired invisibility cloak built with **Python, OpenCV, and NumPy**.

Capture your background, step back into the frame with a bright red cloth, and watch the cloth disappear in real time. ✨

<br>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge\&logo=opencv\&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Image%20Processing-013243?style=for-the-badge\&logo=numpy\&logoColor=white)
![Webcam](https://img.shields.io/badge/Input-Webcam-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

<br>

[🚀 Quick Start](#-quick-start) •
[🎬 How It Works](#-how-it-works) •
[🎮 Controls](#-controls) •
[🧠 Algorithm](#-the-algorithm) •
[🛠️ Tech Stack](#️-tech-stack)

</div>

---

## ✨ What is this?

**Real-Time Invisibility Cloak** is a Computer Vision project that creates a Harry Potter–style invisibility effect using a webcam.

The application detects a **bright red cloth** in the live camera feed and replaces the detected cloth pixels with a previously captured background.

Everything else—including your **face, body, walls, and furniture**—remains visible.

No Machine Learning.
No GPU.
No Internet.

Just **OpenCV + NumPy + Computer Vision magic.** 🪄

> *"Any sufficiently advanced technology is indistinguishable from magic."*

---

## 🎬 How It Works

The complete processing pipeline:

```text
┌──────────────┐
│    Webcam    │
│    Input     │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ Capture Background  │
│ Median of Frames    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Convert BGR → HSV   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Strict Red Detection│
│ Dual HSV Range      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Largest Connected   │
│ Component Selection │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Morphological       │
│ Cleanup + Blur      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Temporal Mask       │
│ Smoothing           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Background          │
│ Alpha Blending      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ ✨ Invisible Cloak  │
└─────────────────────┘
```

---

# 🚀 Quick Start

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Vaishnavi3515/Real_Time_Clock.git
cd Real_Time_Clock
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If required, you can manually install the libraries:

```bash
pip install opencv-python numpy
```

---

## 4️⃣ Run the Project

```bash
python invisibility_cloak.py
```

The webcam will open automatically.

### ⚠️ Important

When the application starts:

> **Step out of the camera frame for approximately 3 seconds.**

The program captures multiple frames and creates a clean background reference using the **median of the captured frames**.

After that:

> Step back into the frame with a **bright red cloth** and enjoy the invisibility effect. ✨

---

# 🎮 Controls

While the application is running:

| Key | Action                                   |
| :-: | ---------------------------------------- |
| `r` | 🔄 Re-capture the background             |
| `s` | 📸 Save the current output as a snapshot |
| `m` | 🧪 Toggle the cloak mask debug window    |
| `q` | ❌ Quit the application                   |

Snapshots are automatically saved inside:

```text
snapshots/
```

Example filename:

```text
cloak_YYYYMMDD-HHMMSS.png
```

---

# 🧠 The Algorithm

## 1. Background Capture

When the application starts, it asks you to move out of the camera frame.

For approximately **3 seconds**, the webcam continuously captures frames.

Instead of using just one frame, the program calculates the **median across all captured frames**:

```python
background = np.median(np.array(frames), axis=0).astype(np.uint8)
```

### Why use the median?

Using the median helps reduce:

* Camera noise
* Small lighting variations
* Temporary movement

The result is a cleaner static background.

---

## 2. Mirror the Camera Feed

Every webcam frame is flipped horizontally:

```python
frame = cv2.flip(frame, 1)
```

This creates a natural **mirror-like camera view**.

The background is also captured after flipping so that the live frame and background remain correctly aligned.

---

## 3. Convert BGR to HSV

OpenCV captures frames in the **BGR color space**.

The frame is converted to HSV:

```python
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
```

HSV separates:

```text
H → Hue        (Color)
S → Saturation (Color intensity)
V → Value      (Brightness)
```

This makes color-based object detection more reliable.

---

## 🔴 4. Strict Red Cloth Detection

Red is special in the HSV color space because it appears at both ends of the hue range.

The project uses two HSV ranges:

```python
LOWER1 = np.array([0, 110, 80])
UPPER1 = np.array([8, 255, 255])

LOWER2 = np.array([172, 110, 80])
UPPER2 = np.array([180, 255, 255])
```

The final mask combines both ranges:

```python
mask1 | mask2
```

### Why use high saturation?

The project requires:

```text
Saturation ≥ 110
```

This helps reject:

* Skin tones
* Brown objects
* Warm-colored furniture
* Weak red reflections

A bright red cloth generally has much higher saturation than human skin.

---

# 🧩 5. Largest Connected Component

Even after color detection, there may still be unwanted red objects in the frame.

For example:

* A red poster
* A small red object
* Red patterns on clothing
* Tiny noise pixels

The program uses:

```python
cv2.connectedComponentsWithStats()
```

It then keeps only the:

> 🟥 **Largest connected red region**

This significantly improves the cloak detection.

```text
Detected Red Pixels

🔴 🔴      🔴

🔴 🔴 🔴

      🔴

        ↓

Keep Only Largest Region

🔴 🔴 🔴
🔴 🔴 🔴
🔴 🔴 🔴
```

---

# 📏 6. Area Threshold

A very small red object should not be considered a cloak.

The program checks whether the largest red region is at least:

```text
0.5% of the total frame area
```

The condition:

```python
areas.max() < frame_area * 0.005
```

If the detected region is smaller than this threshold, the program ignores it.

This helps eliminate:

* Random red pixels
* Small background objects
* Image noise

---

# 🧹 7. Morphological Cleanup

After selecting the cloth region, the mask is cleaned using morphological operations.

### Morphological Opening

```python
cv2.MORPH_OPEN
```

Used to remove:

* Small noise
* Tiny isolated pixels

### Morphological Closing

```python
cv2.MORPH_CLOSE
```

Used to fill:

* Small holes
* Gaps inside the detected cloth

The project uses a:

```text
3 × 3 Kernel
```

---

# 🌫️ 8. Soft Edge Blending

A hard mask can make the invisibility effect look unnatural.

To create smoother edges, the project applies:

```python
cv2.GaussianBlur()
```

The mask is blurred before compositing.

This creates a smoother transition:

```text
Hard Edge

████████│ Background

Soft Edge

██████▓▒░ Background
```

Result:

✨ More natural invisibility effect
✨ Less visible cutout boundaries
✨ Smoother transitions between the cloth and background

---

# ⏳ 9. Temporal Mask Smoothing

Lighting changes or fast movement can sometimes cause the cloth detection to flicker.

To reduce this problem, the current mask is combined with the previous frame's mask:

```python
m = cv2.bitwise_or(m, prev_mask)
```

The result is blurred again to smooth the transition.

This helps:

* Reduce flickering
* Keep the cloak region stable
* Prevent temporary holes in the mask

---

# 🪄 10. Background Replacement

Once the cloak mask is created, the detected cloth is replaced with the stored background.

The project uses alpha blending:

```python
alpha = mask.astype(np.float32) / 255.0
```

The output is calculated using:

```text
Output =
Live Frame × (1 − Mask)
+
Background × Mask
```

Where the mask is bright:

> 🪄 Show the background.

Where the mask is dark:

> 👤 Show the live camera frame.

---

# ⚡ Features

* 📷 Real-time webcam processing
* 🪄 Harry Potter–style invisibility effect
* 🔴 Strict dual-range HSV red detection
* 👤 Skin-tone rejection using saturation filtering
* 🧩 Largest connected-component detection
* 📏 0.5% minimum cloak area threshold
* 🧹 Morphological mask cleanup
* 🌫️ Gaussian blur for soft edges
* ⏳ Temporal mask smoothing
* 🖼️ Automatic background capture
* 📸 Save output snapshots
* 🧪 Debug mask visualization
* 🔄 Background recapture without restarting
* 🪞 Mirror-style webcam preview
* ⚡ Lightweight and runs locally

---

# 🛠️ Tech Stack

| Technology | Purpose                               |
| ---------- | ------------------------------------- |
| 🐍 Python  | Core programming language             |
| 👁️ OpenCV | Webcam processing and Computer Vision |
| 🔢 NumPy   | Image arrays and numerical operations |
| 📷 Webcam  | Real-time video input                 |

---

# 🖥️ Camera Configuration

The application attempts to use:

```text
Resolution: 640 × 480
```

Configured using:

```python
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

---

# 📁 Project Structure

```text
Real_Time_Clock/
│
├── invisibility_cloak.py     # Main application
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── .gitignore
│
└── snapshots/                # Saved output images
    └── cloak_YYYYMMDD-HHMMSS.png
```

> The `snapshots` directory is automatically created by the application if it does not already exist.

---

# 🎯 Best Results

For the best invisibility effect:

### 🔴 Use a Bright Red Cloth

Recommended:

* Solid red cloth
* High saturation
* Minimal patterns

Avoid:

* Dark red
* Orange-red
* Patterned fabric
* Low-saturation colors

---

### 💡 Keep the Lighting Stable

The background should not significantly change after capture.

Avoid:

* Turning lights on or off
* Moving lamps
* Opening or closing bright windows

---

### 📷 Keep the Camera Stable

The background and live frame need to remain aligned.

Avoid moving:

* The laptop
* The webcam
* The camera angle

---

### 👕

Avoid Wearing Red

The program detects red pixels.

If your shirt contains the same shade of red as the cloak:

> Your shirt may disappear too. 😄

---

# 🧪 Debug Mode

Press:

```text
m
```

The application opens a second window:

```text
Cloak mask
```

The mask shows:

```text
White → Detected cloak region

Black → Everything else
```

This is useful for:

* Testing HSV detection
* Adjusting lighting
* Checking the cloth detection
* Debugging mask problems

---

# 🎨 Tuning the Red Detection

If your cloth is not detected correctly, you can modify these values inside:

```text
invisibility_cloak.py
```

```python
LOWER1 = np.array([0, 110, 80])
UPPER1 = np.array([8, 255, 255])

LOWER2 = np.array([172, 110, 80])
UPPER2 = np.array([180, 255, 255])
```

### If your face is accidentally detected

Increase the saturation threshold:

```text
110 → Higher value
```

### If your red cloth is not detected

Try slightly lowering the saturation threshold.

---

# ⚠️ Limitations

Like any color-based Computer Vision system, the project can be affected by:

* Poor lighting
* Shadows on the cloth
* Very dark red fabric
* Objects with similar red colors
* Fast movement
* Wrinkled cloth
* Movement in the background after background capture
* Camera movement

For best results:

> Use a bright red cloth, stable lighting, and a static background.

---

# 🚀 Future Improvements

Possible future upgrades include:

* 🎨 Support for multiple cloak colors
* 🟢 Green and 🔵 blue cloth detection
* 🎥 Video recording
* 🖥️ GUI interface
* 🎚️ Interactive HSV sliders
* 🤖 AI-based object segmentation
* 🧠 Deep Learning–based background replacement
* 📱 Web application version
* ⚡ GPU acceleration

---

# 📚 Concepts Demonstrated

This project demonstrates important Computer Vision concepts:

* Real-Time Video Processing
* Color Space Conversion
* HSV Color Segmentation
* Binary Image Masking
* Connected Component Analysis
* Morphological Operations
* Gaussian Blurring
* Temporal Smoothing
* Alpha Blending
* Background Replacement

---

# 🤝 Contributing

Contributions, improvements, and ideas are welcome!

### Steps

1. Fork this repository

2. Create a new branch

```bash
git checkout -b feature-name
```

3. Make your changes

4. Commit your changes

```bash
git commit -m "Add new feature"
```

5. Push the branch

```bash
git push origin feature-name
```

6. Create a Pull Request

---

# 📜 License

This project is currently intended for **educational and learning purposes**.

Feel free to:

* ⭐ Star the repository
* 🍴 Fork the project
* 📚 Learn from the implementation
* 🛠️ Build improvements on top of it

---

# 👩‍💻 Author

<div align="center">

### **Vaishnavi Gupta**

🐍 Python Developer
👁️ Computer Vision Enthusiast
🪄 Exploring OpenCV and Image Processing

<br>

⭐ **If you enjoyed this project, consider giving the repository a star!**

<br>

### *"Magic is just technology we haven't understood yet."* ✨

<br>

**Built with ❤️ using Python, OpenCV, and NumPy**

</div>
