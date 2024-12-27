# Use Node.js to build the React app
FROM node:18 AS build

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the app and build
COPY . .
RUN npm run build

# Use Nginx to serve the built React app
FROM nginx:latest AS production
COPY --from=build /app/build /usr/share/nginx/html

# Expose Nginx port
EXPOSE 80
