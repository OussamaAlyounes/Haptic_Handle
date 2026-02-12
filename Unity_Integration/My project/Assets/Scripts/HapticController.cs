using UnityEngine;
using System;
using System.Runtime.InteropServices;
public class HapticController : MonoBehaviour
{
    private float totalTrialTime = 0f;
    // public float k_spring = 50.0f; // Stiffness of the spring (Adjust this)
    // public float k_spring_damper = 1.0f;    
    // public float k_torque = 1.0f;
    // public float k_torque_damper = 1.0f;
    public Vector3 k_force_spring = new Vector3(50f, 50f, 50f); // Higher Z to fight gravity
    public Vector3 k_force_damper = new Vector3(1f, 1f, 1f);    // Higher Z to stop heavy oscillations
    public Vector3 k_torque_spring = new Vector3(1f, 1f, 1f);
    public Vector3 k_torque_damper = new Vector3(1f, 1f, 1f);
    public float gravityOffset = 3f; // Newtons - tune this until the arm "floats"
    public Vector3 torqueWire = new Vector3(0.01f, 0.0f, 0.08f); // Newton-meters - to compensate the torque caused by the wires
    public static IntPtr virtuoseContext = IntPtr.Zero;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    // We store the position here so other scripts can read it
    public static Vector3 haptionPosition = Vector3.zero;
    public static Vector3 haptionOffset = Vector3.zero;
    // private static float[] haptionZeroPos = new float[7]{0.234047f, 0.0109161f, -0.01446901f, 
    //                                                      0.01778358f, 0.6750224f, -0.0187347f, 0.737345f};
    private static float[] haptionZeroPos = new float[7]{0.2482343f, -0.01810248f, -0.05825624f, 
                                                         0.1185921f, 0.6642925f, -0.06192293f, 0.7354026f};
    
    public float deadzoneRadius = 0.02f; // 2 cm deadzone
    int force_flag;
    void Start()
    {
        // Connect to Haption device using localhost address
        // Note: Update this address to the device IP if needed (default device IP: 192.168.100.53 UDP 5000)
        string deviceName = "127.0.0.1#53210";

        // Open connection to Haption device via NativeMethods wrapper
        IntPtr context = NativeMethods.virtOpen(deviceName);
        // Debug.Log(context);
        // Debug.Log("virtGetErrorCode "+ NativeMethods.virtGetErrorMessage(NativeMethods.virtGetErrorCode(context)));

        if(context != IntPtr.Zero)
        {
            virtuoseContext = context;
            // Set the maximum force the motors are allowed to output 

            NativeMethods.virtSetPowerOn(virtuoseContext, 1); // switch on force feedback

            // Set command type to impedance control (mode 3)
            // Valid modes: 0 (NONE), 3 (IMPEDANCE), 4 (VIRTMECH), 5 (ARTICULAR), 6 (ARTICULAR_IMPEDANCE)
            force_flag = NativeMethods.virtSetCommandType(virtuoseContext, 3);
            
            NativeMethods.virtSetForceFactor(virtuoseContext, 1.0f);
            NativeMethods.virtStartLoop(virtuoseContext);
            Debug.Log("connected");
        }
        else Debug.LogError("faild to connect to Haption device!");
        
        // Initial calibration to set the offset
        CalibrateCenter();

        // send the haption to the center position
        // NativeMethods.virtSetPosition(virtuoseContext, haptionZeroPos);
    }
    public static void CalibrateCenter()
    {
        // Capture the current raw position as the new 'Zero'
        // float[] pos = new float[7];
        // NativeMethods.virtGetPosition(virtuoseContext, pos);
        // NativeMethods.virtGetPhysicalPosition(virtuoseContext, pos);
        haptionOffset = new Vector3(haptionZeroPos[1], haptionZeroPos[2], -haptionZeroPos[0]);
        // haptionOffset = new Vector3(0.2275134f, 0.003969247f, -0.03929439f); // hardcoded offset for consistent testing
    }

    // Update is called once per frame
    void Update()
    {
        if (virtuoseContext != IntPtr.Zero)
        {
            float[] pos = new float[7]; // Haption uses 7 floats (pos + orientation)
            // NativeMethods.virtGetPosition(virtuoseContext, pos);
            NativeMethods.virtGetPhysicalPosition(virtuoseContext, pos);
            float[] speed = new float[6];
            NativeMethods.virtGetSpeed(virtuoseContext, speed);
            
            totalTrialTime += Time.deltaTime;
            // if(totalTrialTime > 1f)
            // {
            //     Debug.Log("Haption Position: " + pos[0] + ", " + pos[1] + ", " + pos[2] 
            //                                    + pos[3] + ", " + pos[4] + ", " + pos[5] + ", " + pos[6]);
            //     totalTrialTime = 0f;
            // }

            // adding a force effect to pull back to center 
            // it should be based on the offset from the center, regardless of the deadzone
            float[] forceFeedback = new float[6]{0,0,0,0,0,0};

            // Force = -Stiffness * (CurrentPosition - Center)
            // We use the negative because we want to PULL back to center
            forceFeedback[0] = -k_force_spring.x * (pos[0] - haptionZeroPos[0]) - k_force_damper.x * speed[0];
            forceFeedback[1] = -k_force_spring.y * (pos[1] - haptionZeroPos[1]) - k_force_damper.y * speed[1];
            forceFeedback[2] = -k_force_spring.z * (pos[2] - haptionZeroPos[2]) - k_force_damper.z * speed[2] + gravityOffset;
            // forceFeedback[0] = 1.0f;
            // forceFeedback[1] = 1.0f;
            // forceFeedback[2] = 1.0f;

            // Now handle orientation (torque)
            // 1. Current Orientation (indices 3,4,5,6 of your pos array)
            Quaternion currentRot = new Quaternion(pos[3], pos[4], pos[5], pos[6]);
            // 2. Target Orientation (from your haptionZeroPos)
            Quaternion targetRot = new Quaternion(haptionZeroPos[3], haptionZeroPos[4], haptionZeroPos[5], haptionZeroPos[6]);
            // 3. Calculate Error Rotation
            Quaternion errorRot = targetRot * Quaternion.Inverse(currentRot);
            // 4. Convert to Angle-Axis
            float angle = 0f;
            Vector3 axis = Vector3.zero;
            errorRot.ToAngleAxis(out angle, out axis);
            // Angle is 0-360, we need it to be -180 to 180 for the spring
            if (angle > 180) angle -= 360;
            // 5. Apply Torque Spring (using a different k for torque)
            Vector3 torqueSpring = axis * (angle * Mathf.Deg2Rad);

            forceFeedback[3] = torqueSpring.x * k_torque_spring.x - k_torque_damper.x * speed[3] + torqueWire.x; // to compensate the torque caused by the wires
            // the sign is negative is the gravit causes a torque in the negative Y direction and the wire is not affecting the torque in Y
            forceFeedback[4] = torqueSpring.y * k_torque_spring.y - k_torque_damper.y * speed[4] - gravityOffset/10f;
            forceFeedback[5] = torqueSpring.z * k_torque_spring.z - k_torque_damper.z * speed[5] - torqueWire.z;

            // trim all forces to a maximum value for safety
            float maxSafetyForce = 5.0f; // Newtons
            for (int i = 0; i < 6; i++) forceFeedback[i] = Mathf.Clamp(forceFeedback[i], -maxSafetyForce, maxSafetyForce);

            NativeMethods.virtSetForce(virtuoseContext, forceFeedback);

            if(totalTrialTime > 2f)
            {   
                // Debug.Log("Haption Position: " + pos[0] + ", " + pos[1] + ", " + pos[2]);
                // Debug.Log("Haption Force: " + forceFeedback[0] + ", " + forceFeedback[1] + ", " + forceFeedback[2]);
                float[] forceFeedback1 = new float[6]{1,1,1,0,0,0};
                int result = NativeMethods.virtGetForce(virtuoseContext, forceFeedback1);
                // Debug.Log("Get Force result: " + result);
                // Debug.Log("Haption Force received: " + forceFeedback1[0] + ", " + forceFeedback1[1] + ", " + forceFeedback1[2]);
                // Debug.Log("Set Force result: " + result1);
                // force_flag = NativeMethods.virtGetCommandType(virtuoseContext, result);
                // Debug.Log("Set Force flag: " + force_flag);

                // int startResult = NativeMethods.virtStartLoop(virtuoseContext);
                // Debug.Log("VirtStart Result: " + startResult);

                totalTrialTime = 0f;
            }

            // NativeMethods.virtWaitForSynch(virtuoseContext);
            // Mapping Haption (X, Y, Z) to Unity (X, Y, Z)
            // Note: You might need to swap axes depending on how your Haption is mounted
            Vector3 rawInput = new Vector3(pos[1], pos[2], -pos[0]) - haptionOffset;

            // Apply deadzone
            float distance = rawInput.magnitude;

            if (distance < deadzoneRadius)
            {
                haptionPosition = Vector3.zero;
            }
            else
            {
                // Subtract the deadzone and normalize so motion is smooth
                // This prevents a "jump" the moment you cross the 2cm border
                haptionPosition = rawInput.normalized * (distance - deadzoneRadius);
                // haptionPosition = rawInput;
            }
        }
    }

    void OnApplicationQuit()
    {
        // NativeMethods.virtSetPowerOn(virtuoseContext, 0); // turn off the power
        NativeMethods.virtClose(virtuoseContext);
        virtuoseContext = IntPtr.Zero;
        Debug.Log("closed connection");
    }
}
