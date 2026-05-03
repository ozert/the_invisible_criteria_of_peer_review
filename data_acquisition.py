import os
import hydra
from dotenv import load_dotenv
from rich.progress import track
from utils.openreview_api import OpenReview
from conf.config import DataAcquisitionConfig
from hydra.core.config_store import ConfigStore
from utils.colored_prints import ColoredPrint
from mongodb.mongo_data_access import MongoAbstractor
from utils.utils import db_entry_preparation_for_submission, db_entry_preparation_for_review, db_entry_preparation_for_decision, db_entry_preparation_for_meta_review, db_entry_preparation_for_official_comment, db_entry_preparation_for_rebuttal
from utils.logging_module import get_logger

load_dotenv()

logger = get_logger(__name__, log_file='logs/data_acquisition.log')

# Register the config so Hydra knows about it
cs = ConfigStore.instance()
cs.store(group="schema",
         name="data_acquisition",
         node=DataAcquisitionConfig,
         package="_global_")

@hydra.main(config_path="conf", version_base=None, config_name="config")
def main(configuration_details: DataAcquisitionConfig) -> None:
    
    console_printer = ColoredPrint()
    console_printer.print_colored_art("OpenReview  Data  Acquisition", font="standard", style="bold italic cyan")
    logger.info("-"*25 + " NEW RUN " + "-"*25)
    logger.info("Starting the 'OpenReview Data Acquisition Pipeline'.")

    #Initialize Mongo
    logger.info("Initializing MongoDB connection.")
    mongodb = MongoAbstractor(db_name=configuration_details["mongodb"]["db_name"])
    
    #Initialize OpenReview Client
    logger.info("Initializing OpenReview client.")
    openreview = OpenReview()
    
    #selected_venues = configuration_details["open_review_conf"]["root_conference_names"]
    #logger.info(f"Selected Venues: {selected_venues}")

    #Data Acquisition of a Venue
    logger.info("Pulling all venue names.")
    
    # All Venues
    all_venues = openreview.get_all_venues()
    logger.info(f"Number of Venues: {len(all_venues)}")

    ####################################################

    # Data acquisition for a specific venue

    logger.info(f"Pulling data for: '{configuration_details.iclr_2024_venue}'")
    venue_id = configuration_details.iclr_2024_venue
    api_version = configuration_details.open_review_conf.api_version


    # All Submissions
    logger.info("Pulling submissions for the venue.")
    all_submissions = openreview.get_all_submissions(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of submissions: {len(all_submissions)}")
    # Save All Submissions to MongoDB
    logger.info("Saving submissions to MongoDB.")
    for submission in track(all_submissions, description="Save All Submissions to MongoDB"):    
        prepared_data = db_entry_preparation_for_submission(submission, api_version=api_version)
        mongodb.safe_insert_one(collection_name="submissions", data=prepared_data)

    # Accepted Submissions
    logger.info("Pulling accepted submissions for the venue.")
    accepted_submissions = openreview.get_accepted_submissions(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of accepted submissions: {len(accepted_submissions)}")
    logger.info("Saving accepted submissions to MongoDB.")
    # Save Accepted Submissions to MongoDB
    for submission in track(accepted_submissions, description="Save Accepted Submissions to MongoDB"):    
        prepared_data = db_entry_preparation_for_submission(submission, api_version=api_version)
        mongodb.safe_insert_one(collection_name="accepted_submissions", data=prepared_data)

    # Withdrawn Submissions
    logger.info("Pulling withdrawn submissions for the venue.")
    withdrawn_submissions = openreview.get_withdrawn_submissions(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of withdrawn submissions: {len(withdrawn_submissions)}")
    logger.info("Saving withdrawn submissions to MongoDB.")
    # Save Withdrawn Submissions to MongoDB
    for submission in track(withdrawn_submissions, description="Save Withdrawn Submissions to MongoDB"):    
        prepared_data = db_entry_preparation_for_submission(submission, api_version=api_version)
        mongodb.safe_insert_one(collection_name="withdrawn_submissions", data=prepared_data)

    # Desk-Rejected Submissions
    logger.info("Pulling desk-rejected submissions for the venue.")
    desk_rejected_submissions = openreview.get_desk_rejected_submissions(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of desk-rejected submissions: {len(desk_rejected_submissions)}")
    logger.info("Saving desk-rejected submissions to MongoDB.")
    # Save Desk-Rejected Submissions to MongoDB
    for submission in track(desk_rejected_submissions, description="Save Desk-Rejected Submissions to MongoDB"):    
        prepared_data = db_entry_preparation_for_submission(submission, api_version=api_version)
        mongodb.safe_insert_one(collection_name="desk_rejected_submissions", data=prepared_data)

    # All Reviews
    logger.info("Pulling reviews for the venue.")
    all_reviews = openreview.get_all_reviews(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of reviews: {len(all_reviews)}")
    logger.info("Saving reviews to MongoDB.")
    # Save All Reviews to MongoDB
    for review in track(all_reviews, description="Save Reviews to MongoDB"):    
        prepared_data = db_entry_preparation_for_review(review, api_version=api_version)
        mongodb.safe_insert_one(collection_name="reviews", data=prepared_data)

    # All Rebuttals
    logger.info("Pulling rebuttals for the venue.")
    all_rebuttals = openreview.get_all_rebuttals(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of rebuttals: {len(all_rebuttals)}")
    logger.info("Saving rebuttals to MongoDB.")
    # Save All Rebuttals to MongoDB
    for rebuttal in track(all_rebuttals, description="Save Rebuttals to MongoDB"):    
        prepared_data = db_entry_preparation_for_rebuttal(rebuttal, api_version=api_version)
        mongodb.safe_insert_one(collection_name="rebuttals", data=prepared_data)

    # Official Comments
    logger.info("Pulling official comments for the venue.")
    official_comments = openreview.get_official_comments(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of official comments: {len(official_comments)}")
    logger.info("Saving official comments to MongoDB.")
    # Save Official Comments to MongoDB
    for comment in track(official_comments, description="Save Official Comments to MongoDB"):
        prepared_data = db_entry_preparation_for_official_comment(comment)
        mongodb.safe_insert_one(collection_name="official_comments", data=prepared_data)

    # Meta Reviews
    logger.info("Pulling meta reviews for the venue.")
    meta_reviews = openreview.get_meta_reviews(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of meta reviews: {len(meta_reviews)}")
    logger.info("Saving meta reviews to MongoDB.")
    # Save Meta Reviews to MongoDB
    for meta_review in track(meta_reviews, description="Save Meta Reviews to MongoDB"):
        prepared_data = db_entry_preparation_for_meta_review(meta_review)
        mongodb.safe_insert_one(collection_name="meta_reviews", data=prepared_data)

    # All Decisions
    logger.info("Pulling decisions for the venue.")
    all_decisions = openreview.get_all_decisions(api_version=api_version, venue_id=venue_id)
    logger.info(f"Number of decisions: {len(all_decisions)}")
    logger.info("Saving decisions to MongoDB.")
    # Save Decisions to MongoDB
    for decision in track(all_decisions, description="Save Decisions to MongoDB"):
        prepared_data = db_entry_preparation_for_decision(decision)
        mongodb.safe_insert_one(collection_name="decisions", data=prepared_data)

    logger.info("-"*25 + " END RUN " + "-"*25)
    
if __name__ == "__main__":
    main()