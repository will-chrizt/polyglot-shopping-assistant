// FILE: query-service.js
// This is the new microservice that uses AWS Bedrock.
// It fetches data from product-service and uses an AI model to answer queries.
// -----------------------------------------------------------------------------

const express_query = require('express');
const axios = require('axios');
const { BedrockRuntimeClient, InvokeModelCommand } = require("@aws-sdk/client-bedrock-runtime");

const app_query = express_query();
const PORT_QUERY = 8002;
const PORT_PRODUCT = 8001; // Define the port for the product service

// --- AWS Bedrock Configuration ---
// IMPORTANT: Configure your AWS credentials in your environment.
// Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION.
// For example, in your terminal:
// export AWS_REGION="us-east-1"
// export AWS_ACCESS_KEY_ID="YOUR_KEY"
// export AWS_SECRET_ACCESS_KEY="YOUR_SECRET"

const bedrockClient = new BedrockRuntimeClient({
    region: process.env.AWS_REGION || "us-east-1", // Change to your preferred region
});

// The ARN of the model you want to use.
// Claude 3 Sonnet is a great general-purpose model.
const modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0";

/**
 * Creates a structured prompt for the AI model.
 * @param {string} userQuery - The user's natural language question.
 * @param {Array<Object>} products - The list of products from the product-service.
 * @returns {string} The formatted prompt.
 */
const createPrompt = (userQuery, products) => {
    const productList = JSON.stringify(products, null, 2);

    return `Human: You are a helpful and friendly e-commerce assistant. Your task is to answer the user's query based ONLY on the provided list of products. Do not invent products or details. If the answer cannot be found in the product list, say that you don't have enough information.

Here is the list of available products:
<products>
${productList}
</products>

Here is the user's query:
<query>
${userQuery}
</query>

Please provide a clear and concise answer.

Assistant:`;
};

// --- API Endpoint for AI-powered Queries ---
app_query.get('/query', async (req, res) => {
    const userQuery = req.query.q;

    if (!userQuery) {
        return res.status(400).json({ error: 'Query parameter "q" is required.' });
    }

    console.log(`Received query: "${userQuery}"`);

    try {
        // Step 1: Fetch all products from the product-service
        console.log('Fetching products from product-service...');
        const productHost = process.env.PRODUCT_SERVICE_HOST || 'product-service';
        const productURL = `http://${productHost}:${PORT_PRODUCT}/products`;
        const productResponse = await axios.get(productURL);
        const products = productResponse.data;
        console.log(`Successfully fetched ${products.length} products.`);

        // Step 2: Create a prompt for the AI model
        const prompt = createPrompt(userQuery, products);

        // Step 3: Prepare the payload for the AWS Bedrock API
        const payload = {
            modelId,
            contentType: "application/json",
            accept: "application/json",
            body: JSON.stringify({
                anthropic_version: "bedrock-2023-05-31",
                max_tokens: 2000,
                messages: [{
                    role: "user",
                    content: [{
                        type: "text",
                        text: prompt
                    }]
                }]
            }),
        };

        // Step 4: Invoke the model via AWS Bedrock
        console.log('Sending query to AWS Bedrock...');
        const command = new InvokeModelCommand(payload);
        const apiResponse = await bedrockClient.send(command);

        // Step 5: Decode and parse the response from the model
        const decodedResponseBody = new TextDecoder().decode(apiResponse.body);
        const responseBody = JSON.parse(decodedResponseBody);
        
        if (responseBody.content && responseBody.content.length > 0) {
            const answer = responseBody.content[0].text;
            console.log('Received answer from Bedrock.');
            res.json({
                query: userQuery,
                answer: answer.trim()
            });
        } else {
            throw new Error("Invalid response structure from Bedrock API");
        }

    } catch (error) {
        console.error('An error occurred:', error.message);
        // Differentiate between service connection errors and other errors
        if (error.code === 'ECONNREFUSED') {
            res.status(500).json({ error: 'Could not connect to the product-service. Is it running?' });
        } else {
            res.status(500).json({ error: 'Failed to process your query.', details: error.message });
        }
    }
});

const HOST_QUERY = process.env.HOST_QUERY || '0.0.0.0';
app_query.listen(PORT_QUERY, HOST_QUERY, () => {
  console.log(`✅ AI Query service running at http://${HOST_QUERY}:${PORT_QUERY}`);
  console.log(`🚀 Try it out: http://${HOST_QUERY}:${PORT_QUERY}/query?q=what+is+a+good+budget+laptop+for+coding`);
});
