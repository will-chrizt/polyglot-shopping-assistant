# =================================================================
# Stage 1: Build the application using Maven
# =================================================================
FROM maven:3.8.5-openjdk-17 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the pom.xml first to leverage Docker's layer caching.
# Dependencies will only be re-downloaded if pom.xml changes.
COPY pom.xml .

# Download all dependencies
RUN mvn dependency:go-offline

# Copy the rest of the source code
COPY src ./src

# Package the application, skipping the tests
RUN mvn clean package -DskipTests

# =================================================================
# Stage 2: Create the final, lightweight runtime image
# =================================================================
FROM eclipse-temurin:17-jre-focal

# Set the working directory
WORKDIR /app

# Create a non-root user for security purposes
RUN groupadd --system spring && useradd --system --gid spring spring
USER spring

# Copy the executable JAR from the build stage
# Make sure the <artifactId> and <version> in your pom.xml match the JAR name
COPY --from=build /app/target/cart-0.0.1-SNAPSHOT.jar app.jar

# Expose the port the application runs on
EXPOSE 8080

# The command to run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
