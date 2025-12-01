FROM eclipse-temurin:17-jdk AS build

WORKDIR /app

# Install Maven
RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*

# Copy pom.xml first for dependency caching
COPY pom.xml .

# Download dependencies (this layer will be cached if pom.xml doesn't change)
RUN mvn dependency:go-offline -B

# Copy source code (only after dependencies are cached)
COPY src ./src

# Build the application with Spring Boot plugin
RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Download OpenTelemetry Java Agent
RUN curl -L -o opentelemetry-javaagent.jar \
    https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v1.32.0/opentelemetry-javaagent.jar

# Copy the built jar (Spring Boot creates executable JAR)
COPY --from=build /app/target/*.jar app.jar

# Create non-root user
RUN addgroup --system --gid 1001 spring
RUN adduser --system --uid 1001 --gid 1001 spring
RUN chown spring:spring opentelemetry-javaagent.jar
USER spring

# Expose port
EXPOSE 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:9000/auth/health || exit 1

# Start the application with OpenTelemetry Java Agent
CMD ["java", "-javaagent:opentelemetry-javaagent.jar", "-jar", "app.jar"]




