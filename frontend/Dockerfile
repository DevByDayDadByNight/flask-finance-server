# Use Node.js for development
FROM node:18 AS development

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps



# Pass the REACT_APP_API_URL build argument
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}


# Copy the rest of the app
COPY . .

# Remove the old build folder before building
RUN rm -rf build
RUN npm run build

# Expose React development server port
EXPOSE 3000
