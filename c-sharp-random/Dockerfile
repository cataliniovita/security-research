# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Allows building from either the project directory or repo root.
# If building from repo root, pass: --build-arg PROJECT_DIR=c-sharp-random/RandomVulnDemo
ARG PROJECT_DIR=RandomVulnDemo

COPY ${PROJECT_DIR}/RandomVulnDemo.csproj ${PROJECT_DIR}/
RUN dotnet restore ${PROJECT_DIR}/RandomVulnDemo.csproj

COPY ${PROJECT_DIR}/ ${PROJECT_DIR}/
WORKDIR /src/${PROJECT_DIR}
RUN dotnet publish -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://0.0.0.0:8080
ENTRYPOINT ["dotnet", "RandomVulnDemo.dll"]


