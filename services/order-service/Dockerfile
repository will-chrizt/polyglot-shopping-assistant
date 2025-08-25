FROM maven:3.9-eclipse-temurin-17 as build
WORKDIR /build
COPY pom.xml .
RUN mvn -q -e -DskipTests dependency:resolve
COPY src ./src
RUN mvn -q -e -DskipTests package
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /build/target/*.jar /app/app.jar
ENV PORT=8003
EXPOSE 8003
CMD ["java", "-jar", "/app/app.jar"]
