# ArtFace - Real-Time Event Face Recognition


ArtFace provides a seamless photo experience for event guests, allowing them to receive photos of themselves as they are taken by the event photographer. In the full version of the project, guests can scan a QR code at the event to connect to a bot, allowing them to easily upload their facial photos and receive relevant event pictures in real-time.

## Table of Contents

- [Features](#features)
- [Algorithm Overview](#algorithm-overview)
- [Handling Suspected Users](#handling-suspected-users)
- [License](#license)

## Features

- **Real-Time Image Processing**: Immediate detection and categorization of faces from uploaded images.
- **Dynamic Learning**: Continuous model retraining as more images are added, improving identification accuracy.
- **Guest Access**: Guests receive images that include them throughout the event, not just at the end.
- **Handling Uncertainty**: Use of a hierarchical approach to manage low-confidence matches efficiently.
- **YOLOv7**: Uses for face detection and recognition.

## Algorithm Overview

The core of ArtFace lies in its adaptive algorithm that learns and improves as more data is collected. However, this learning process presents challenges, especially with early-stage misclassifications.

1. **Image Processing Pipeline**:

   - When an image is uploaded, the system processes it to detect faces.
   - If a face is **not recognized**, it is registered as a **new user**.
   - If a face **matches** an existing user with a **high probability**, the model retrains itself using this image to improve recognition of that user.
   - If the match probability is **moderate**, the system records that the user is seen but waits for more data.
   - If the match probability is **low**, the face is added to a **suspected user** list for further re-evaluation.

2. **Handling Misclassifications**:

   - **Early Phase Issue**: During initial learning, the system may misclassify unknown faces as new users, even if they belong to someone already registered. This leads to the creation of multiple profiles for the same person.
   - To solve this, **suspicious users** are held temporarily and reconsidered as the system learns more. The key idea is to re-evaluate these users after additional training has occurred, allowing the model to decide more confidently if they are new users or match an existing user.

## Handling Suspected Users

A unique approach to handling suspected identities is using a **forest structure**, where:

- Each tree **root** represents a **confirmed user**.
- Each **descendant node** represents a **suspected duplicate** of the user above it.
- **Suspected users** can themselves be suspected duplicates of other suspected users, creating a multi-level structure.

### Forest-Based Re-Evaluation Process

When the tree height becomes too deep for optimal running time, a re-evaluation process begins. During this process, the system re-checks the similarity between nodes, either merging them with existing users or confirming them as independent users. Finally, root nodes are also compared to each other, and if high similarities are found, they are merged.

## License

This project is licensed under the MIT License.
