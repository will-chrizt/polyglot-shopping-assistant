No, i mean, what was the issue with my ingress resource, i was able to see the frontend with product list but when i tried /products with curl i didn't get the product list.



Show thinking
Of course. The issue with your Ingress was a classic and very subtle configuration problem caused by a single, incorrect annotation.

The problem was the line nginx.ingress.kubernetes.io/rewrite-target: / in your ingress.yaml file. This annotation created a global rewrite rule that applied to every path, causing unintended behavior for your backend services.

The Cause: Global Path Rewrite
Think of the rewrite-target: / annotation as a building-wide mail redirection rule. You accidentally told the post office (the NGINX Ingress controller), "For any mail addressed to this building, ignore the apartment number and deliver everything to the lobby (/)."

Why /products Failed
This is what happened when you tried to curl .../products:

Your request for /products arrived at the Ingress controller.

The Ingress matched the path: /products rule, which correctly pointed to your product-service.

Before forwarding the request, it applied the global rewrite rule, changing the path from /products to /.

It then sent a request for / to your product-service.

Your product-service application has no code to handle the root / path, so it correctly responded with a Cannot GET / error.

Why the Frontend (/) Worked
This is why the situation was confusing. When you accessed the main page:

Your request for / arrived at the Ingress controller.

The Ingress matched the path: / rule, pointing to your frontend-service.

It applied the rewrite rule, changing the path from / to /. In this one specific case, the path remained unchanged.

It sent the request for / to your frontend-service, which had a handler for the root path and served the webpage correctly.

The Solution
The solution was to remove the nginx.ingress.kubernetes.io/rewrite-target: / annotation entirely. Your backend services were already designed to listen on the correct paths (e.g., your product-service was listening on /products). By removing the rewrite rule, the Ingress now forwards the original paths unchanged, allowing each service to handle its requests correctly.
