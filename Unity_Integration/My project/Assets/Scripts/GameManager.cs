using UnityEngine;
using TMPro; // Needed for TextMeshPro components
using System.Collections; // Required for Coroutines

public class GameManager : MonoBehaviour
{
    // Assign these in the Inspector
    public TMP_InputField IdInput;
    public TMP_Dropdown experimentTypeDropdown; // You'll need to create this element
    public GameObject inputPanel; // Reference to the UI panel containing the inputs
    public GameObject pathManager;
    // Data Storage
    public static string subjectId;
    public static string experimentType; // "Trial", "Time", "ThermalTime", "ThermalError"
    public static bool patternDetected = true;
    private string currentPattern;
    private string patterChoice1 = "lr";
    private string patterChoice2 = "ci";
    // Unfreeze the ball
    public BallMovement ballMovement;
    public GameObject endMessagePanel;
    public Rigidbody ballRb;
    // timer
    public TextMeshProUGUI timerText; // Use the TMPro type
    public TextMeshProUGUI hapticInfoText;
    public void StartTrial()
    {
        // 1. Capture Data
        // if (int.TryParse(IdInput.text, out int age))
        // {
        //     subjectAge = age;
        // }
        // else
        // {
            // subjectAge = -1; // Flag for invalid entry
        // }
        subjectId = IdInput.text;
        
        // Get the selected text from the dropdown
        experimentType = experimentTypeDropdown.options[experimentTypeDropdown.value].text;

        Debug.Log($"Starting Trial: Id {subjectId}, Type {experimentType}");

        // 2. Hide UI and Start Trial Logic (e.g., enable input on the Ball)
        inputPanel.SetActive(false);

        // start the timer of the experiment is timer
        if (!experimentType.Contains("Thermal")) // Ensure this string matches your dropdown option
        {
            ballMovement.timerIsActive = true;
            timerText.gameObject.SetActive(true); // Activate the UI text element
            // Debug.Log("Timer was selected");
        }
        if (experimentType == "Haptic Thermal") // turn on thermal cold from the beginning of the vibration detection phase
        {
            ballMovement.PublishThermalCommand("cccc");
        }
        // Debug.Log(experimentType.ToString());
        // Start the choice input loop to activate the vibration only for the correct type of experiments
        StartCoroutine(WaitForChoiceAndStart());
    }

    IEnumerator WaitForChoiceAndStart()
    {
        // Debug.Log("CHOICE PHASE: Press 1 (Pattern LR) or 2 (Pattern CI). Press SPACE to start.");
        
        // open the gripper completely
        ballMovement.PublishExpansionCommand(6);

        hapticInfoText.text = "Press 1 or 2 to feel the vibration pattern.";
        // swap the patterns randomly only if the experiment is not a trial
        if (Random.value > 0.5f && experimentType != "Trial")
        {
            patterChoice1 = "ci";
            patterChoice2 = "lr";
        }
        // else nothing happens and we do not swap the assignment of the patterns

        while (experimentType != "No Haptic") // Loop to activate the vibration if haptic is present
        {
            // --- CHOICE INPUT ---
            if (Input.GetKeyDown(KeyCode.Alpha1) || Input.GetKeyDown(KeyCode.Keypad1))
            {
                // Set choice to 1 (Pattern LR)
                // ballMovement.currentChoice = 1;
                ballMovement.ballRenderer.material = ballMovement.ballMaterialBlack;
                currentPattern = patterChoice1;
                if (experimentType == "Trial") hapticInfoText.text = "This is Left-Right Pattern. Remember it!\nPress 2 for the other pattern or press <space> to move next";
                else hapticInfoText.text = "If this is the Circular pattern, press <space>\nand start the experiment.";
                // Send the vibration command for left-right pattern
                ballMovement.PublishVibrationCommand(currentPattern);
            }
            else if (Input.GetKeyDown(KeyCode.Alpha2) || Input.GetKeyDown(KeyCode.Keypad2))
            {
                // Set choice to 2 (Pattern CI)
                // ballMovement.currentChoice = 2;
                ballMovement.ballRenderer.material = ballMovement.ballMaterialWhite;
                currentPattern = patterChoice2;
                if (experimentType == "Trial") hapticInfoText.text = "This is Circular Pattern. Remember it!\nPress 1 for the other pattern or press <space> to move next";
                else hapticInfoText.text = "If this is the Circular pattern, press <space>\nand start the experiment.";
                // Send the vibration command for circular pattern
                ballMovement.PublishVibrationCommand(currentPattern);
            }

            // --- START TRIAL INPUT ---
            if (Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Return))
            {
                patternDetected = (currentPattern == "ci");
                // Debug.Log($"STARTING TRIAL (Mode: {experimentType}) with Pattern: CI");
                break; // Exit the coroutine
            }
            yield return null; // Wait one frame before checking input again
        }
        //
        // Unfreeze the ball and start the main trial
        ballRb = ballMovement.GetComponent<Rigidbody>();
        ballRb.constraints = RigidbodyConstraints.None;
        // make the path visible again
        pathManager.SetActive(true);
        // BallMovement.trialRunning = true;
        hapticInfoText.gameObject.SetActive(false);
        // close the gripper command
        ballMovement.PublishExpansionCommand(0);
        yield break;
    }
}