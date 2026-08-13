# Universal-Jamming-Gripper
A custom modeled, 3D-printed 4-axis robotic arm with a pneumatic universal jamming gripper. Controlled using an ESP32 micro-controller and any generic video game controller, this project combines mechanical design, power electronics, embedded control, and soft robotics to adaptively pick and place irregular objects.

<img width="900" height="675" alt="Jamming-Gripper-Demo" src="https://github.com/user-attachments/assets/c07f4834-d918-417e-b082-65bfff9ae45c" />


## Components & Specifications

| Subsystem | Component | Specifications & Engineering Function |
| --- | --- | --- |
| **Microcontroller** | ESP-WROOM-32 | Central controller, I2C communication, and GPIO triggers. |
| **PWM Driver** | PCA9685 Module | 16-Channel 12-bit PWM expansion board driving joint servos over I2C. |
| **Joint Actuators** | 40KG Digital Servos | High-torque metal-gear servos providing 4 degrees of freedom. |
| **Mechanical Bearings** | AXK5578 Thrust Bearings | Needle roller bearings absorbing axial loads at primary joint linkages. |
| **Pneumatic Vacuum** | VN-T1 Micro Diaphragm Pump | 12V DC vacuum pump used to suck air from the gripper chamber. |
| **Pneumatic Control** | 2-Way Solenoid Valve | 12V DC valve used to vent atmospheric pressure into the membrane for release. |
| **Isolation Circuit** | Optocoupler Relay Modules | Optically isolates 5V micro-controller logic from 12V inductive switching noise. |
| **Power Supply 1** | 5V 10A DC Power Adapter | High-amperage dedicated power rail for the PCA9685 and joint servos. |
| **Power Supply 2** | 12V DC Power Adapter | Dedicated supply for high-current pneumatic pump and solenoid actuation. |
| **Teleoperation Input** | Nintendo Switch Controller | Wired input controller mapped for real-time Cartesian/joint control. |
| **Fasteners** | M3 Hardware + Brass Inserts | Socket-head machine screws paired with thermal heat-set brass inserts. |

---

## System Architecture

```text
                        ┌──────────────────────────────┐
                        │ Nintendo Switch Controller   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼ 
                        ┌──────────────────────────────┐
                        │      ESP32 Controller        │
                        └──────┬────────────────┬──────┘
                               │                │
                    (I2C Line) │                │ (GPIO Signals)
                               ▼                ▼
┌────────────────────────────────────────┐   ┌────────────────────────────────────────┐
│      PCA9685 12-Bit PWM Driver         │   │       Optocoupler Relay Modules        │
└──────────────────┬─────────────────────┘   └──────────────────┬─────────────────────┘
                   │                                            │
   (5V 10A Rail)   │                               (12V Rail)   │
                   ▼                                            ▼
┌────────────────────────────────────────┐   ┌────────────────────────────────────────┐
│    4x 40KG High-Torque Joint Servos    │   │      12V Vacuum Pump & Solenoid        │
└────────────────────────────────────────┘   └──────────────────┬─────────────────────┘
                                                                │ (Air Tubing)
                                                                ▼
                                             ┌────────────────────────────────────────┐
                                             │      Universal Jamming Gripper         │
                                             └────────────────────────────────────────┘
