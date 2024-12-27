# Use Node.js to build the React app
FROM node:18 AS build

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Copy the rest of the app and build
COPY . .
RUN npm run build

# Use Nginx to serve the built React app
FROM nginx:latest AS production
COPY --from=build /app/build /usr/share/nginx/html

# Expose Nginx port
EXPOSE 80
