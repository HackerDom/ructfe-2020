FROM gradle:4.7.0-jdk8-alpine

COPY . /app
WORKDIR /app
RUN ["./gradlew", "jar"]
ENTRYPOINT ["java", "-jar", "./build/libs/keeper-1.0-SNAPSHOT.jar"]
