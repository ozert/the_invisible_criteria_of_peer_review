import sys
import os

sys.path.append(os.getcwd())

from llm_pipeline.chains.chains import Chains

class LLMAdaptor:
    """
    LLMAdaptor is a class designed to interact with a language model for various natural language processing tasks. 
    It provides methods to separate questions from a review string and summarize a conversation history.
    Attributes:
        model (Chains): An instance of the Chains class initialized with the specified deployment name and temperature.
    Methods:
        __init__(deployment_name: str, temperature: float = 0.0):
            Initializes the LLMAdaptor with a specific deployment name and temperature. Validates the deployment name 
            against a predefined list of valid names.
        separate_questions_from_a_review(question_field_str: str) -> list:
            Separates individual questions from a given review string using the language model.
        summarize_conversation(conversation_history: list) -> str:
            Summarizes the conversation history provided as a list of dictionaries, where each dictionary represents 
            a message in the conversation.
    """
    
    def __init__(self, deployment_name:str, cloud_host:str, temperature:float=0.0):
        
        valid_deployment_names = [
            "gemini-2.5-pro",
            "text-embedding-005",
            "gpt-5-mini-2025-08-07",
            "gpt-4o-mini-2024-07-18",
            "o3-mini-2025-01-31",
            "deepseek-r1",
            "gpt-4",
            "gpt-4o",
            "meta.llama4-maverick-17b-instruct-v1:0",
            "anthropic.claude-v3-haiku",
            "claude-sonnet-4@20250514",
            "claude-3-7-sonnet@20250219",
            "gemini-2.0-flash-lite",
            "gpt-oss-120b",
            "rlab-qwq-32b",
            "gemini-2.5-flash"
        ]
        assert deployment_name in valid_deployment_names, f"Invalid deployment name: {deployment_name}. Must be one of {valid_deployment_names}."
        self.model = Chains(deployment_name=deployment_name, temperature=temperature, cloud_host=cloud_host)

    def assign_topic(self, input_params:dict):
        """
        Assigns topics to a list of input parameters using the topic assignment functionality.
        Args:
            input_params (dict): A list of input data for prompt template.
        Returns:
            dict: LLM output.
        """
        
        assigned_topic = self.model.assign_topic_to_separated_question(input_params=input_params)

        return assigned_topic
    
    def evaluate_question_separation(self, separated_question_data:str):
        """
        Evaluates the separation of questions from the provided input string.
        This method uses the model's `separate_questions` function to process
        the input string and return the separated questions.
        Args:
            separated_question_data (str): A string containing the question data
                to be separated.
        Returns:
            list: A list of separated questions as determined by the model.
        """
        
        separated_questions = self.model.judge_question_separation(separated_question_data=separated_question_data)

        return separated_questions
    
    def evaluate_topic_assignment(self, topic_assignment_data:str):
        """
        Evaluates the topic assignment for the given question data.
        This method uses the model's `judge_topic_assignment` function to process
        the provided question data and determine the topic assignments.
        Args:
            topic_assignment_data (str): The input data containing separated questions
                to be evaluated for topic assignment.
        Returns:
            Any: The result of the topic assignment evaluation, as determined by the model.
        """
        
        
        separated_questions = self.model.judge_topic_assignment(topic_assignment_data=topic_assignment_data)

        if not isinstance(separated_questions["is_valid_topic"], bool):
            raise TypeError("Expected separated_questions['is_valid_topic'] to be a bool.")

        return separated_questions
    
    def separate_questions_from_a_review(self, question_field_str:str):
        """
        Separates individual questions from a given review string.
        This method takes a string containing questions and uses the model to 
        separate them into individual questions.
        Args:
            question_field_str (str): A string containing questions to be separated.
        Returns:
            list: A list of separated questions.
        """
        
        separated_questions = self.model.separate_questions(questions=question_field_str)

        return separated_questions
    
    def noninformant_review_detection(self, raw_question:str):
        """
        Detects whether a given question is non-informative using the model's filtering mechanism.
        Args:
            raw_question (str): The raw input question to be analyzed.
        Returns:
            Any: The output of the model's non-informant question filtering process.
        """
                
        filtering_output = self.model.non_informant_question_filtering(raw_question=raw_question)

        return filtering_output
    
    def assign_correspondance_level_to_a_text(self, question:list):
        """
        Assigns a correspondence level based on the provided question.
        This method is intended to analyze the input question and determine
        the appropriate correspondence level. The specific implementation
        details and logic for the assignment are defined in the 
        CorrespondanceAssignmentTemplate.
        Args:
            question (list): The input question for which the correspondence 
                            level needs to be assigned.
        Returns:
            str: The method returns one of the sections specified in its correspondance list.
        """

        correspondance_level = self.model.assign_correspondance_level(question=question)

        return correspondance_level["data"]

    def summarize_conversation(self, conversation_history:list):
        """
        Summarizes the conversation history using the model.
        Args:
            conversation_history (list): A list of dictionaries representing the conversation history. 
                                         Each dictionary contains key-value pairs where the key is the 
                                         speaker (e.g., "user", "assistant") and the value is the message.
        Returns:
            str: A summary of the conversation generated by the model.
        """
        context = "\n".join(f"{key.capitalize()}: {value}" for d in conversation_history for key, value in d.items())
        conversation_summary = self.model.summarize_conversation(conversation_history=context)

        return conversation_summary
    
    def expand_question_context(self, input_data:dict):
        
        expanded_question_data = self.model.expand_context(input_data=input_data)

        return expanded_question_data

if __name__ == "__main__":
    adaptor_gemini2_5_pro = LLMAdaptor(deployment_name="gemini-2.5-pro", temperature=0.0)
 
    print("Testing context expander with Gemini 2.5 Pro")
    input_data = {"question":"Can you provide more insight into NEKM?", "review":"NEKM is a novel method for training neural networks with one hidden layer. The authors propose a bilevel optimization framework that jointly optimizes the weights of the network and the parameters of a kernel function. The method is shown to outperform traditional training methods on several benchmark datasets, including MNIST and CIFAR-10. The authors also provide theoretical guarantees for the convergence of their algorithm and demonstrate its effectiveness in learning complex decision boundaries. Overall, NEKM is a promising approach for training neural networks that leverages the power of kernel methods to improve performance and generalization."}
    simulation_of_a_question = [{'role': 'user', 'content': input_data}]
    conversation_summary = adaptor_gemini2_5_pro.expand_question_context(input_data=input_data)
    [print(item) for item in conversation_summary]
