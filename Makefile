# Define the Docker image and container name
IMAGE_NAME=digesto-hybrid-search:beta-1.4
CONTAINER_NAME=digesto-hybrid-search-container

clean: 
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	
# Define the command to run the Docker container
run: clean
	docker run -it --name $(CONTAINER_NAME) -v $(PWD):/app --gpus all $(IMAGE_NAME)

run-no-gpu: clean
	docker run -it --name $(CONTAINER_NAME) -v $(PWD):/app $(IMAGE_NAME)

# To stop the Docker container
stop:
	docker stop $(CONTAINER_NAME)