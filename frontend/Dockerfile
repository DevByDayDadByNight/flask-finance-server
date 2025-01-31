# Use Node.js for development
FROM node:18 AS development

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install



# Pass the REACT_APP_API_URL build argument
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}


# Copy the rest of the app
COPY . .

# Expose React development server port
EXPOSE 3000
