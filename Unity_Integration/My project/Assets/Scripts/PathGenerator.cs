using UnityEngine;
using System.Collections.Generic; // Needed for the List container

public class PathGenerator : MonoBehaviour
{
    // Public variables adjustable in the Unity Inspector
    public int randomSeed = 42;         // CRUCIAL: Ensures the path is always the same.
    public int numSegments = 50;        // Total number of segments (points) in the path
    public float segmentLength = 2.0f;  // The distance along the Z-axis between segments
    public float maxLateralOffset = 3.0f; // Max deviation in the X and Y plane (how curvy the tube is)

    public float tubeRadius;// = 1f;     // The inner radius (half the tube's width)
    public float wallThickness = 0.2f;  // Thickness of the tube wall
    public Material tubeMaterial;
    public Material tubeErrorMaterial;
    public Material tubeHoleMaterial;       // Drag a material here from the Inspector (e.g., standard grey)
    public int segmentsPerSection = 16; // Defines how circular the cross-section is
    // Store the generated points so the ball tracking script can use them
    public List<Vector3> pathPoints = new List<Vector3>();
    public GameObject ballObject;
    private float ballRadius;
    void Start()
    {
        GeneratePath();
        GameObject tubeObject = new GameObject("NavigationTube");
        tubeObject.transform.SetParent(this.transform); // Keep it clean in the hierarchy
        SphereCollider ballCollider = ballObject.GetComponent<SphereCollider>();
        ballRadius = ballCollider.radius* ballObject.transform.localScale.x;
        // Debug.Log("ballRadius = " + ballRadius.ToString());
        // Debug.Log("tubeRadius = " + tubeRadius.ToString()); 

        // BuildTubeMesh();
        DrawSimplePipeSegments(tubeObject.transform);
        CreateStartEndGates();
    }

    void GeneratePath()
    {
        // 1. Initialize the Random Generator with the fixed seed
        Random.InitState(randomSeed); 
        
        // 2. Start at the origin (0, 0, 0)
        Vector3 currentPos = Vector3.zero;
        pathPoints.Add(currentPos); // Add the starting point

        for (int i = 0; i < numSegments; i++)
        {
            // 3. Calculate random offset: The path primarily moves forward (Z), 
            //    but slightly curves in the X and Y directions.
            
            float xOffset = Random.Range(-maxLateralOffset, maxLateralOffset);
            float yOffset = Random.Range(-maxLateralOffset, maxLateralOffset);
            
            // To prevent sharp turns, we only allow a small delta (change) from the current position.
            // We use Lerp to smoothly move the offset towards the randomized target.
            // Note: This is a simplified smoothing method.

            Vector3 nextRandomTarget = currentPos + new Vector3(xOffset, yOffset, segmentLength);
            
            // 4. Smooth the movement and move forward along Z-axis
            Vector3 nextPos = Vector3.Lerp(currentPos, nextRandomTarget, 0.25f); // 0.25f defines the smoothing strength
            nextPos.z = currentPos.z + segmentLength; // Ensure consistent forward progress

            // 5. Add the point and prepare for the next iteration
            pathPoints.Add(nextPos);
            
            // OPTIONAL: Visualize the points to confirm the path is fixed
            // GameObject marker = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            // marker.transform.position = nextPos;
            // marker.transform.localScale = Vector3.one * 0.2f;
            // marker.GetComponent<Renderer>().material.color = Color.blue;
            
            currentPos = nextPos;
        }
    }
        
    // Alternative: A series of simple overlapping pipe segments (less complex)
    void DrawSimplePipeSegments(Transform parent)
    {
        for (int i = 0; i < pathPoints.Count - 1; i++)
        {
            Vector3 start = pathPoints[i];
            Vector3 end = pathPoints[i + 1];
            
            Vector3 center = (start + end) / 2f;
            Quaternion rotation = Quaternion.LookRotation(end - start);
            float length = Vector3.Distance(start, end);
            
            // Create a simple cylinder (pipe segment)
            GameObject pipe = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            pipe.transform.SetParent(parent);
            pipe.transform.position = center;
            pipe.transform.rotation = rotation*Quaternion.Euler(90, 0, 0);
            pipe.tag = "TubeWall"; // all pipe segments should have the same tag so that we use it in case of a trigger
            // Scale the cylinder to fit the length and radius
            float scaleFactor = tubeRadius + wallThickness;
            pipe.transform.localScale = new Vector3(scaleFactor*2, length / 2f, 
                                                    scaleFactor*2);
            // pipe.transform.localScale = new Vector3((tubeRadius)*2, length / 2f, 
            //                                         (tubeRadius)*2);

            // Add Collider/Trigger: Remove the default Collider and add a Trigger component
            Destroy(pipe.GetComponent<Collider>());
            // CapsuleCollider outerTrigger = pipe.AddComponent<CapsuleCollider>();
            // outerTrigger.isTrigger = true;
            // outerTrigger.radius = tubeRadius + wallThickness;
            // outerTrigger.height = length;
            
            pipe.GetComponent<Renderer>().material = tubeMaterial;
            
            // Create a slightly thinner cylinder inside for the "hollow" effect
            GameObject innerHole = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            // GameObject innerHole = pipe.transform.GetChild(0).gameObject; // Assuming the hole is the first child
            innerHole.transform.SetParent(pipe.transform);
            innerHole.transform.localPosition = Vector3.zero;
            innerHole.transform.localRotation = Quaternion.identity;
            // innerHole.transform.localScale = new Vector3(0.9f, 1.05f, 0.9f); // Slightly smaller hole
            float relativeInnerScale = tubeRadius / scaleFactor;
            // innerHole.transform.localScale = new Vector3(tubeRadius * 0.9f, 1.05f, tubeRadius * 0.9f); // Slightly smaller hole
            innerHole.transform.localScale = new Vector3(relativeInnerScale, 1.15f, // Divide by the pipe's Y scale factor to normalize it back to 1.05 local height
                                                         relativeInnerScale);
            // innerHole.transform.localScale = new Vector3(0.9f, 1.0f, 0.9f); // Local scale relative to the pipe
            // innerHole.GetComponent<Renderer>().material.color = Color.black; 
            innerHole.GetComponent<Renderer>().material = tubeHoleMaterial;
            
            // Remove the hole's collider
            Destroy(innerHole.GetComponent<Collider>());

            // Create the new inner collider
            CapsuleCollider centerTrigger = pipe.AddComponent<CapsuleCollider>();

            // --- NEW: CREATE UN-SCALED COLLIDER PARENT ---
            // GameObject colliderParent = new GameObject("ColliderParent");
            // colliderParent.transform.SetParent(pipe.transform); // Child of pipe
            // colliderParent.transform.localScale = Vector3.one; // CRUCIAL: Reset scale to (1,1,1)
            // colliderParent.transform.localPosition = Vector3.zero;
            // colliderParent.transform.localRotation = Quaternion.Euler(0, 90, 0);
            // // --- CENTERLINE SENSOR LOGIC (on the unscaled parent) ---
            // CapsuleCollider centerTrigger = colliderParent.AddComponent<CapsuleCollider>();
            
            centerTrigger.isTrigger = true;
            // scalling as the radius is being scalled according to the parent pipe
            float ballMesh = 0.5f;
            centerTrigger.radius = (tubeRadius - ballRadius - ballMesh)/(scaleFactor*2);//tubeRadius - ballRadius; 
            centerTrigger.height = length; //length
            // Debug.Log("centerRadius = " + centerTrigger.radius.ToString()); 

            // Assign the new tag
            centerTrigger.gameObject.tag = "SafeZoneTrigger";
        }
    }

    private void CreateStartEndGates()
    {
        // Ensure the path exists before creating gates
        if (pathPoints.Count < 2) return; 

        // --- START GATE (Positioned at the first path point) ---
        GameObject startGate = new GameObject("StartGate");
        startGate.transform.SetParent(this.transform);
        startGate.transform.position = pathPoints[0]; // Position at the first path point
        
        BoxCollider startTrigger = startGate.AddComponent<BoxCollider>();
        startTrigger.isTrigger = true;
        // Make the gate wide enough to ensure the ball is caught
        startTrigger.size = new Vector3(tubeRadius * 4, tubeRadius * 4, 0.1f); 
        
        startGate.tag = "StartGate"; // NEW TAG for detection

        // --- END GATE (Positioned at the last path point) ---
        Vector3 endPos = pathPoints[pathPoints.Count - 1]; // Last path point
        
        GameObject endGate = new GameObject("EndGate");
        endGate.transform.SetParent(this.transform);
        endGate.transform.position = endPos; 
        
        BoxCollider endTrigger = endGate.AddComponent<BoxCollider>();
        endTrigger.isTrigger = true;
        endTrigger.size = new Vector3(tubeRadius * 4, tubeRadius * 4, 0.1f); 
        
        endGate.tag = "EndGate"; // NEW TAG for detection
        
        // Optional: Hide the gates visually by disabling the Mesh Renderer component
        // Since these are simple BoxColliders without a MeshRenderer by default,
        // they are already invisible, but we can ensure it:
        // startGate.GetComponent<Renderer>().enabled = false;
        // endGate.GetComponent<Renderer>().enabled = false;
    }

    public void SetAllTubeSegmentsColor(Material newMaterial)
    {
        // Find the main tube container object
        Transform tubeParent = transform.Find("NavigationTube");
        if (tubeParent == null)
        {
            Debug.LogError("NavigationTube container not found!");
            return;
        }

        // Loop through every single pipe segment (child of the container)
        foreach (Transform child in tubeParent)
        {
            // Get the Renderer component which controls the color
            Renderer renderer = child.GetComponent<Renderer>();

            // Ensure we only set the color for the pipe segments (not the innerHole)
            // We identify the pipe segments by their tag
            if (child.CompareTag("SafeZoneTrigger") && renderer != null)
            {
                renderer.material = newMaterial;
                // Debug.Log("color changed!");
            }
        }
    }
}