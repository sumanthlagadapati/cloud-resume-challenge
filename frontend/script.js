// URL to your Lambda Function URL or API Gateway
const apiUrl = "YOUR_LAMBDA_FUNCTION_URL_HERE";

document.addEventListener("DOMContentLoaded", () => {
    // We only try to fetch if the URL has been set (to avoid console errors while building)
    if (apiUrl !== "YOUR_LAMBDA_FUNCTION_URL_HERE") {
        fetchVisitorCount();
    } else {
        document.getElementById("visitor-count").innerText = "[PENDING DEPLOYMENT]";
    }
});

async function fetchVisitorCount() {
    try {
        const response = await fetch(apiUrl, {
            method: 'POST', // Or GET based on your Lambda configuration
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const count = data.count;

        // Update the HTML element
        document.getElementById("visitor-count").innerText = count;
    } catch (error) {
        console.error("Could not fetch visitor count:", error);
        document.getElementById("visitor-count").innerText = "[Counter Error]";
    }
}
