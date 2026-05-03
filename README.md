### Setting Up the Environment from Scratch

Follow these steps to set up the environment from scratch:

1. **Create a Conda Environment**  
    Open your terminal and run the following command to create a new Conda environment named `paper_env` with Python 3.12:  
    ```bash
    conda create -n paper_env python=3.12 -y
    ```

2. **Activate the Environment**  
    Activate the newly created environment:  
    ```bash
    conda activate paper_env
    ```

3. **Install Poetry**  
    Use `pip` to install Poetry, a dependency management tool:  
    ```bash
    pip install poetry
    ```

4. **Install Dependencies**  
    Run the following command to install all dependencies specified in the `pyproject.toml` file:  
    ```bash
    poetry install --no-root
    ```

That's it! Your environment is now ready to use. 🎉

### Using MongoDB on macOS

To set up and use MongoDB with Docker on macOS, follow these steps:

1. **Start Colima**  
    Ensure Colima is running to provide a Docker runtime:  
    ```bash
    colima start
    ```

2. **Create a Docker Volume**  
    Create a Docker volume to persist MongoDB data:  
    ```bash
    docker volume create paper-volume-docker
    ```

3. **Run MongoDB in a Docker Container**  
    Start a MongoDB container using the created volume:  
    ```bash
    docker run -d --name paper-mongo-container -p 27017:27017 -v paper-volume-docker:/data/db mongo
    ```

4. **Verify MongoDB is Running**  
    Check if the MongoDB container is running:  
    ```bash
    docker ps
    ```

    You should see `paper-mongo-container` listed in the output.

5. **Connect to MongoDB**  
    Use a MongoDB client or library to connect to the database at `localhost:27017`.


### Restoring MongoDB from a Backup

To restore a MongoDB database from a `.gz` backup file, follow these steps:

1. **Copy the Backup File to the Container**  
    Use the `docker cp` command to copy the `.gz` backup file into the MongoDB container:  
    ```bash
    docker cp openreview_db_backup.gz paper-mongo-container:/tmp/openreview_db_backup.gz
    ```

2. **Restore the Backup**  
    Execute the following command to restore the MongoDB database from the `.gz` backup file:  
    ```bash
    docker exec -it paper-mongo-container mongorestore \
        --gzip \
        --archive=/tmp/openreview_db_backup.gz
    ```

Your MongoDB database has now been restored from the backup file. 🎉
### MongoDB Commands Overview

Here’s how to view your database and its collections in MongoDB:

1. **Enter the Docker Container**  
    To access the MongoDB container, use the following command:  
    ```bash
    docker exec -it paper-mongo-container bash
    ```
2. **Start `mongosh`**  
    To interact with MongoDB, start the `mongosh` shell:  
    ```bash
    mongosh
    ```

3. **List Databases**  
    Run the following command to see all databases:  
    ```bash
    show dbs
    ```
    Example Output:  
    ```
    admin                     40.00 KiB
    config                   108.00 KiB
    local                     72.00 KiB
    openreview_db_iclr_2024  173.54 MiB
    openreview_db_iclr_2025  318.20 MiB
    ```

4. **Switch to a Database**  
    Use this command to switch to `openreview_db_iclr_2024`:  
    ```bash
    use openreview_db_iclr_2024
    ```
    Example Output:  
    ```
    switched to db openreview_db_iclr_2024
    ```

5. **List Collections**  
    To view all collections in `openreview_db_iclr_2024`, run:  
    ```bash
    show collections
    ```
    Example Output:  
    ```
    accepted_submissions
    decisions
    desk_rejected_submissions
    meta_reviews
    official_comments
    reviews
    submissions
    withdrawn_submissions
    ```


6. **Count Documents in All Collections**  
    To see the document counts of all collections in `openreview_db_iclr_2024`, use the following script in `mongosh`:  
    ```javascript
    // Connect to the database
    const db = db.getSiblingDB("openreview_db_iclr_2024");

    // Get all collections in the database
    const collections = db.getCollectionNames();

    // Iterate over each collection and count documents
    collections.forEach(collection => {
        const count = db[collection].countDocuments();
        print(`Collection: ${collection}, Document Count: ${count}`);
    });
    ```
    Example Output (ICLR 2024):
    ```
    Collection: desk_rejected_submissions, Document Count: 53
    Collection: accepted_submissions, Document Count: 2260
    Collection: withdrawn_submissions, Document Count: 1656
    Collection: submissions, Document Count: 7404
    Collection: meta_reviews, Document Count: 5781
    Collection: reviews, Document Count: 28028
    Collection: decisions, Document Count: 5780
    Collection: official_comments, Document Count: 70624
    ```
    Example Output (ICLR 2025):
    ```
    Collection: withdrawn_submissions, Document Count: 2979
    Collection: submissions, Document Count: 11672
    Collection: desk_rejected_submissions, Document Count: 70
    Collection: decisions, Document Count: 8727
    Collection: meta_reviews, Document Count: 8727
    Collection: accepted_submissions, Document Count: 3704
    Collection: reviews, Document Count: 46748
    Collection: official_comments, Document Count: 149219
    ```

### MongoDB Database Backup
To create a backup of the openreview_db_iclr_2024 MongoDB database and copy it to your local machine, follow these steps:

1. **Backup the MongoDB Database**

    In order to take a backup of the MongoDB database from a container go to your working directory in Mac then run the following command.

    ```bash
    docker exec paper-mongo-container mongodump \
        --db=openreview_db_iclr_2024 \
        --archive=/data/db/openreview_db_iclr_2024_backup.gz \
        --gzip
    ```
2. **Copy the Backup to Your Local Machine**

    Copy the backup from docker container to Mac.

    ```bash
    docker cp paper-mongo-container:/data/db/openreview_db_iclr_2024_backup.gz data/
    ```
