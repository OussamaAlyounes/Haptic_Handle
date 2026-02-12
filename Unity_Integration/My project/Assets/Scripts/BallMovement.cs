using UnityEngine;
using System.IO;
using System.Collections.Generic;
using NUnit.Framework;
using Unity.Robotics.ROSTCPConnector;
using RosMessageTypes.Std;
using System;

public class BallMovement : MonoBehaviour
{
    // Public variables adjustable in the Unity Inspector
    public float movementSpeed = 5f;
    public float forceMagnitude = 20f;
    public GameObject pathManager;

    // Variables for Color Logic
    private Material defaultTubeMaterial; // Will hold the default green material
    public Material errorTubeMaterial;     // Red material (assigned in Inspector)
    public Material ballMaterialBlack; // Assign Black Material
    public Material ballMaterialWhite; // Assign White Material
    public Renderer ballRenderer;  // A renderer to change the ball's color
    private PathGenerator pathGenerator; // refernce from the path generator to change the color
    private bool isStillSafe = false;

    // Variables for starting and ending the experiment
    public float totalTrialTime = 0f;
    public float timeSpentInError = 0f;
    public int collisionCount = 0;
    public float timeSpentInCollision = 0f;
    private List<float> timeIntervals = new List<float>(); // Stores the duration of each error sequence
    private List<float> errorStartTimepoints = new List<float>(); // Stores the TOTAL TRIAL TIME when the error sequence began (e.g., 15.25s)
    private List<float> errorStartZPositions = new List<float>(); // Stores the Z-coordinate where the error sequence began
    private float currentErrorSequenceStartTime; // Helper variable to mark the start of the current sequence (using Time.time)
    private Vector3 lastPosition;
    public float totalPathLength = 0f;
    private bool trialRunning = false;
    private bool lastFrameWasSafe = true; // Use this to count discrete collision events

    private float collisionPenaltyTimer = 0f; 
    // Vibration publishing settings: pattern and minimum interval between messages while colliding
    public string vibrationPattern = "1111"; // all vibros are on
    public float vibrationInterval = 3f; // seconds
    
    // Tracks the current pipe segment the ball is inside
    private Renderer currentSegmentRenderer = null;
    private Rigidbody rb;
    public Rigidbody BallRigidbody => rb;
    private Vector3 currentHapticInput = Vector3.zero;
    private GameManager gameManager; // Reference to the Manager// panel
    public bool timerIsActive = false;
    private int currentThermalStep = 0;
    // public int currentChoice = 1;
    // ROS connection to WSL
    ROSConnection ros;
    public string expansionTopic = "unity/servo_command";
    public string vibrationTopic = "unity/vibration_command";
    public string thermalTopic = "unity/temperature_command";

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        // Get the ROS connection component
        ros = ROSConnection.GetOrCreateInstance();
        // Register the topics we want to talk to
        ros.RegisterPublisher<Float32Msg>(expansionTopic);
        ros.RegisterPublisher<StringMsg>(vibrationTopic);
        ros.RegisterPublisher<StringMsg>(thermalTopic);        

        // Get the Rigidbody component from the GameObject this script is attached to
        rb = GetComponent<Rigidbody>();
        lastPosition = rb.position;
        // add a color to the ball
        ballRenderer = GetComponent<Renderer>();
        ballRenderer.material = ballMaterialBlack;

        rb.constraints = RigidbodyConstraints.FreezeAll; // to prevent the ball from motion till we press start
        gameManager = FindFirstObjectByType<GameManager>(); // to activate the panel when ending the trial

        if (rb == null)
        {
            Debug.LogError("Rigidbody component not found on the ball object!");
        }
        // to read the functions of the PathGenerator
        pathGenerator = FindFirstObjectByType<PathGenerator>();
        // to ge the object PathManager itself
        // GameObject path = GameObject.Find("PathManager");
        pathManager.SetActive(false);
    }
    // define three functions to send the ros messages to the WSL
    public void PublishExpansionCommand(int distance)
    {
        Float32Msg msg = new Float32Msg(distance);
        ros.Publish(expansionTopic, msg);
        // Debug.Log("Sent to ROS: " + distance);
    }
    public void PublishVibrationCommand(string pattern)
    {
        StringMsg msg = new StringMsg(pattern);
        ros.Publish(vibrationTopic, msg);
        // Debug.Log("Sent to ROS: " + pattern);
    }
    public void PublishThermalCommand(string temperature)
    {
        StringMsg msg = new StringMsg(temperature);
        ros.Publish(thermalTopic, msg);
        // Debug.Log("Sent to ROS: " + temperature);
    }

    // Update is called once per frame
    void Update()
    {
        // keyboard input movement
        // --- 1. GET INPUT (The Placeholder Section) ---
        // For now, read input from the keyboard (WASD or Arrow Keys)
        // float inputX = Input.GetAxis("Horizontal"); // A/D or Left/Right
        // float inputZ = Input.GetAxis("Vertical");   // W/S or Up/Down
        // Y-Axis (Digital On/Off for Simplicity)
        // float inputY = 0.0f;
        // if(Input.GetKey(KeyCode.E)) inputY = 1f; //moveup
        // if(Input.GetKey(KeyCode.Q)) inputY = -1f; //movedown
        // currentHapticInput = new Vector3(inputX, inputY, inputZ).normalized; 
    }
    // FixedUpdate is used for physics calculations
    void FixedUpdate()
    {
        // keyboard input movement
        // if (rb != null && currentHapticInput != Vector3.zero)
        // {
        //     // --- 2. APPLY MOVEMENT FORCE ---
        //     // Apply a continuous force based on the current input direction
        //     rb.AddForce(currentHapticInput * forceMagnitude);
        
        //     // Limit velocity to the set speed to keep the ball controllable
        //     if (rb.linearVelocity.magnitude > movementSpeed)
        //     {
        //         rb.linearVelocity = rb.linearVelocity.normalized * movementSpeed;
        //     }
        // }

        // Haption input movement
        // You might need a much larger 'forceMagnitude' now 
        // because haptionPosition values are usually small (meters).
        rb.AddForce(HapticController.haptionPosition * forceMagnitude);
        if (rb.linearVelocity.magnitude > movementSpeed)
        {
            rb.linearVelocity = rb.linearVelocity.normalized * movementSpeed;
        }

        // Instead of AddForce, we set the velocity based on the handle position
        // This gives you 'Rate Control' but without the 'slippery' inertia
        Vector3 targetVelocity = HapticController.haptionPosition * forceMagnitude;
        // Limit the speed
        if (targetVelocity.magnitude > movementSpeed)
        {
            targetVelocity = targetVelocity.normalized * movementSpeed;
        }

        // Apply directly to the Rigidbody
        rb.linearVelocity = targetVelocity;
        
        /////////////////
        /// end of things to change
        /// /////////////
        if (trialRunning)
        {
            // 1. Total Time Tracking
            totalTrialTime += Time.fixedDeltaTime;
            // Update the UI text with the current trial time
            if (timerIsActive)
            {
                gameManager.timerText.text = $"Time: {totalTrialTime:F1}s";
            }

            // 1. Calculate distance moved since last frame
            float frameDistance = Vector3.Distance(rb.position, lastPosition);
            // 2. Accumulate
            totalPathLength += frameDistance;
            // 3. Update last position for the next frame
            lastPosition = rb.position;

            // Update the temperature cues
            if (GameManager.experimentType == "Haptic Thermal")
            {
                // Phase 0: Start until 40 seconds
                if (currentThermalStep == 0 && totalTrialTime >= 0f)
                {
                    // This runs immediately when the trial starts
                    PublishThermalCommand("cccc");
                    currentThermalStep = 1; // Move to next wait state
                }
                // Phase 1: At 40 seconds
                else if (currentThermalStep == 1 && totalTrialTime >= 20f)
                {
                    PublishThermalCommand("nnnn");
                    currentThermalStep = 2; // Move to next wait state
                }
                // Phase 2: At 80 seconds
                else if (currentThermalStep == 2 && totalTrialTime >= 40f)
                {
                    PublishThermalCommand("hhhh");
                    currentThermalStep = 3; // Final state reached, no more checks
                }
            }
            // 2. Error Time Tracking and Interval Logging
            if (!isStillSafe) // If we are currently in an error state
            {
                // If the error just started (transitioned from safe to unsafe)
                if (lastFrameWasSafe)
                {
                    collisionCount++;
                    
                    // CRITICAL: Capture the Trial Timeline Start Time and Z-position
                    errorStartTimepoints.Add(totalTrialTime); // Store the current elapsed trial time
                    errorStartZPositions.Add(transform.position.z); // Store the Z-position
                    
                    // Also, track the absolute system time to calculate duration later
                    currentErrorSequenceStartTime = Time.time; 
                    
                    // Debug.Log($"NEW Error Sequence Begun at T={totalTrialTime:F2}s, Z={transform.position.z:F2}. Count: {collisionCount}");
                }
            }
            else // If we are currently in a safe state
            {
                // If the safety just started (transitioned from unsafe to safe)
                if (!lastFrameWasSafe)
                {
                    // Calculate the duration and save the interval
                    float errorDuration = Time.time - currentErrorSequenceStartTime;
                    timeIntervals.Add(errorDuration);
                    
                    // Debug.Log($"Error Sequence Ended. Duration: {errorDuration:F3}s");
                }
            }

            // 3. Update the state tracker for the next frame
            // --- VIBRATION: send on entering an error, then at most once per `vibrationInterval` while staying in error ---
            if (!isStillSafe && GameManager.experimentType != "No Haptic")
            {
                if (lastFrameWasSafe)
                {
                    // Just entered error: send vibration immediately
                    PublishVibrationCommand(vibrationPattern);
                    collisionPenaltyTimer = vibrationInterval;
                    // Debug.Log("Vibration sent on error entry!");
                }
                else
                {
                    // Still in error: count down and send again when timer elapses
                    collisionPenaltyTimer -= Time.fixedDeltaTime;
                    if (collisionPenaltyTimer <= 0f)
                    {
                        PublishVibrationCommand(vibrationPattern);
                        collisionPenaltyTimer = vibrationInterval;
                        // Debug.Log("Vibration sent again!");

                    }
                }
            }
            else
            {
                // Reset timer when safe
                collisionPenaltyTimer = 0f;
            }

            lastFrameWasSafe = isStillSafe;
        }
    }

    // --- 1. ENTRY: Ball enters a safe zone segment ---
    void OnTriggerEnter(Collider other)
    {
        // Check if the object we hit is the Safe Zone Sensor
        if (other.gameObject.CompareTag("SafeZoneTrigger")) 
        {
            // Store the renderer of the pipe segment we just entered
            currentSegmentRenderer = other.transform.GetComponent<Renderer>();
            
            // Store the original material if this is the first time we're entering a pipe
            if (defaultTubeMaterial == null && currentSegmentRenderer != null)
            {
                defaultTubeMaterial = currentSegmentRenderer.material;
                // Debug.Log(defaultTubeMaterial.color.ToString());
            }

            // Immediately check if the error timer should stop (if we re-entered safety)
            // Color is set to GREEN here, confirming safety
            if (currentSegmentRenderer != null && !isStillSafe)
            {
                pathGenerator.SetAllTubeSegmentsColor(defaultTubeMaterial);
                isStillSafe = true;
                // Debug.Log("color changing");
                // currentSegmentRenderer.material = defaultTubeMaterial; //defaultTubeMaterial
                // currentSegmentRenderer.material.color = Color.red; //(Simpler, often works)
            }
        }
        // --- END GATE LOGIC ---
        else if (other.gameObject.CompareTag("EndGate") && trialRunning)
        {
            PublishThermalCommand("nnnn"); // so the peltier go back to normal
            // ensure vibration motors are turned off when trial ends
            PublishVibrationCommand("0000");
            trialRunning = false;
            Debug.Log("Trial Finished! Total Time: " + totalTrialTime.ToString("F2") + "s");
            gameManager.endMessagePanel.SetActive(true); // set the final panel to be visible
            rb.constraints = RigidbodyConstraints.FreezeAll;
            // if the ball is still outside the safe zone and touched the end point, then the final time duration was not saved
            if (!isStillSafe)
            {
                // The duration is calculated from the start time of the sequence (currentErrorSequenceStartTime)
                // up to the current total time of the trial.
                float errorDuration = Time.time - currentErrorSequenceStartTime;
                timeIntervals.Add(errorDuration);
            }
            // **CRITICAL STEP:** Call the data saving function here!
            SaveExperimentData(); 
        }
    }

    // --- 2. EXIT: Ball leaves the safe zone segment (This is the visual ERROR signal) ---
    void OnTriggerExit(Collider other)
    {
        // Check if the object we left is the Safe Zone Sensor
        // NOTE: handle exits regardless of experiment type — safety state should not be gated by experiment mode
        if (other.gameObject.CompareTag("SafeZoneTrigger"))
        {
            // The segment color only changes if we AREN'T still touching another segment.
            // This prevents rapid flashing if the ball is crossing a boundary between two segments.

            // Use Physics.OverlapSphere to check if the ball is STILL touching ANY SafeZoneTrigger.
            // If it's not touching anything, the error is confirmed.
            
            Collider[] colliders = Physics.OverlapSphere(transform.position, GetComponent<SphereCollider>().radius);
            isStillSafe = false;
            foreach (Collider c in colliders)
            {
                if (c.gameObject.CompareTag("SafeZoneTrigger"))
                {
                    // Debug.Log("exit");
                    isStillSafe = true;
                    break;
                }
            }
            
            // If the ball left the last safe trigger, trigger the visual error
            if (!isStillSafe && currentSegmentRenderer != null && !GameManager.experimentType.Contains("Thermal"))
            {
                pathGenerator.SetAllTubeSegmentsColor(errorTubeMaterial);

                // currentSegmentRenderer.material = errorTubeMaterial; // CHANGE TO RED
                // currentSegmentRenderer.material.color = Color.red;
                // Debug.Log("ERROR: Left safe path!");
            }
        }

        // --- START GATE LOGIC ---
        else if (other.gameObject.CompareTag("StartGate") && !trialRunning)
        {
            trialRunning = true;
            totalTrialTime = 0f;
            timeSpentInError = 0f;
            collisionCount = 0;
            Debug.Log("Trial Started!");
        }
    }

    void SaveExperimentData()
    {
        // do not save if it is just a trial
        if (GameManager.experimentType == "Trial")
        {
            Debug.Log("Familiarization Trial: Data Recording Skipped.");
            return; // Exit the function immediately
        }

        // 1. Define the file path (saves in the project folder)
        string path = Application.dataPath + "/ExperimentData.csv";
        // Convert Lists to semicolon-separated strings
        string timeIntervalsCSV = string.Join(";", timeIntervals.ConvertAll(f => f.ToString("F3")));
        string errorStartTimepointsCSV = string.Join(";", errorStartTimepoints.ConvertAll(f => f.ToString("F3")));
        string errorStartZPositionsCSV = string.Join(";", errorStartZPositions.ConvertAll(f => f.ToString("F3")));

        // --- Retrieve Global Data ---
        string ID = GameManager.subjectId.ToString();
        string expType = GameManager.experimentType;
        bool detected = GameManager.patternDetected;
        // 2. Format the data line
        // Define the new header
        string header = "ID,ExpType,PatternDetected,TrialTime,CollisionCount,TotalPathLength," +
                        "TimeIntervals_s,ErrorStart_Timeline_s,ErrorStart_Z_m\n";
        //Create the data string (Add Age and ExpType at the beginning)
        string dataLine = $"{ID},{expType},{detected},{totalTrialTime:F3},{collisionCount},{totalPathLength:F2}," +
                          $"{timeIntervalsCSV},{errorStartTimepointsCSV},{errorStartZPositionsCSV}\n";
        // 3. Write/Append to the file
        if (!File.Exists(path))
        {
            // Write header and data if file doesn't exist
            File.WriteAllText(path, header + dataLine);
        }
        else
        {
            // Append data to the existing file
            File.AppendAllText(path, dataLine);
        }
        
        Debug.Log("Data saved successfully.");
    }
    void OnApplicationQuit()
    {
        // Ensure the thermal command is reset when the application quits even if the ball did not reach the end gate
        PublishThermalCommand("nnnn");
        // Also ensure vibration is turned off
        PublishVibrationCommand("0000");
    }
}
