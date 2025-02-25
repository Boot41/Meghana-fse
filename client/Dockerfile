FROM node:18

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with legacy peer deps flag
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

EXPOSE 3000

ENV NODE_ENV=development
ENV VITE_APP_API_URL=http://localhost:8000

# Start Vite dev server with host flag
CMD ["npm", "run", "dev", "--", "--host"]