import os 
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
import sys
load_dotenv()

# Add the parent directory to the system path
sys.path.append(os.getcwd())

from llm_pipeline.prompts.summarization import SummarizationTemplate
from llm_pipeline.prompts.question_separation import QuestionSeparationTemplate
from llm_pipeline.prompts.correspondance_assignment import CorrespondanceAssignmentTemplate
#from llm_pipeline.prompts.context_expander import ContextExpanderTemplate
#from llm_pipeline.prompts.context_satisfaction import ContextSatisfactionTemplate
from llm_pipeline.prompts.judge_question_separation import JudgeQuestionSeparationTemplate
from llm_pipeline.prompts.non_informant_review_filtering import NonInformantQuestionFilteringTemplate
from llm_pipeline.prompts.judge_topic_assignment import JudgeTopicAssignmentTemplate
from llm_pipeline.prompts.topic_assignment import TopicAssignmentTemplate

class Chains():
    def __init__(self, deployment_name:str, temperature:float, cloud_host:str="azure"):
        if cloud_host == "azure":
            self.model = AzureChatOpenAI(deployment_name=deployment_name,
                                        api_version=os.getenv("OPENAI_API_VERSION"),
                                        temperature=temperature,
                                        streaming=True)
        elif cloud_host == "gcp":
            self.model = ChatGoogleGenerativeAI(model=deployment_name, temperature=temperature)
        else:
            raise ValueError("Unsupported cloud_host. Please use 'azure' or 'gcp'.")
        
        self.json_parser = JsonOutputParser()
        self.string_output_parser = StrOutputParser()
                
        self.question_separation_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(QuestionSeparationTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(QuestionSeparationTemplate.USER_PROMPT)])
        
        self.correspondance_assignment_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(CorrespondanceAssignmentTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(CorrespondanceAssignmentTemplate.USER_PROMPT)])
        
        self.summary_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SummarizationTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(SummarizationTemplate.USER_PROMPT)])

        self.non_informant_question_filtering_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(NonInformantQuestionFilteringTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(NonInformantQuestionFilteringTemplate.USER_PROMPT)])
        
        self.judge_question_separation_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(JudgeQuestionSeparationTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(JudgeQuestionSeparationTemplate.USER_PROMPT)])
        
        self.judge_topic_assignment_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(JudgeTopicAssignmentTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(JudgeTopicAssignmentTemplate.USER_PROMPT)])

        self.topic_assignment_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(TopicAssignmentTemplate.SYSTEM_PROMPT),
            HumanMessagePromptTemplate.from_template(TopicAssignmentTemplate.USER_PROMPT)])
        
        #self.context_expander_prompt_template = ChatPromptTemplate.from_messages([
        #    SystemMessagePromptTemplate.from_template(ContextExpanderTemplate.SYSTEM_PROMPT),
        #    HumanMessagePromptTemplate.from_template(ContextExpanderTemplate.USER_PROMPT)])
        
        #self.context_satisfaction_prompt_template = ChatPromptTemplate.from_messages([
        #    SystemMessagePromptTemplate.from_template(ContextSatisfactionTemplate.SYSTEM_PROMPT),
        #    HumanMessagePromptTemplate.from_template(ContextSatisfactionTemplate.USER_PROMPT)])

    def judge_topic_assignment(self, topic_assignment_data:str):
        """
        Evaluates the topic assignment data using a predefined prompt template, a model, 
        and a JSON parser. The method constructs a runnable sequence and invokes it 
        with the provided input data.
        Args:
            topic_assignment_data (str): The input data for topic assignment evaluation.
        Returns:
            dict: The parsed response from the evaluation process.
        """

        runnable = self.judge_topic_assignment_prompt_template | self.model | self.json_parser
        chain = RunnableSequence(runnable)
        response = chain.invoke(topic_assignment_data)

        return response

    def non_informant_question_filtering(self, raw_question:str):
        """
        Filters non-informative questions from the input question string.
        This method processes the given raw question string through a sequence
        of operations involving a prompt template, a model, and a JSON parser.
        It utilizes a `RunnableSequence` to execute these operations and returns
        the processed response.
        Args:
            raw_question (str): The raw question string to be filtered.
        Returns:
            Any: The response generated after processing the input question.
        """
        
        runnable = self.non_informant_question_filtering_prompt_template | self.model | self.json_parser
        chain = RunnableSequence(runnable)
        response = chain.invoke(raw_question)
        
        return response

    def assign_topic_to_separated_question(self, input_params:dict):
        """
        Assigns a topic to a separated question using a sequence of processing steps.
        This method takes a dict of input parameters, processes them through a 
        sequence of runnable components (a topic assignment prompt template, a model, 
        and a JSON parser), and returns the resulting response.
        Args:
            input_params (dict): A list of input parameters to be processed.
        Returns:
            dict: The response generated after processing the input parameters 
                  through the runnable sequence.
        """
        
        #Json parser gives error on some characters like "\". 
        # To avoid this error, we need to replace "\" with "//" in the input parameters before passing it to the chain.
        input_params["sample_text"] = input_params["sample_text"].replace("\\", "//")
        runnable = self.topic_assignment_prompt_template | self.model | self.json_parser
        chain = RunnableSequence(runnable)
        response = chain.invoke(input_params)
        
        return response
    
    def judge_question_separation(self, separated_question_data:str):
        """
        Evaluates the separation of a question using a predefined prompt template, 
        a language model, and a JSON parser.
        Args:
            separated_question_data (str): The input data containing the raw question, 
                                            separated question and expanded context 
                                            for separated question.
        Returns:
            dict: The response generated by the chain, parsed as a JSON object.
        """
                
        runnable = self.judge_question_separation_prompt_template | self.model | self.json_parser
        chain = RunnableSequence(runnable)
        response = chain.invoke(separated_question_data)
        
        return response
            
    def separate_questions(self, questions:str):
        """
        Processes a string containing multiple questions and separates them 
        into individual logical question chunks. This method is designed to 
        handle questions extracted from peer-review text or similar sources.

        Args:
            questions (str): A string containing multiple questions to be separated.

        Returns:
            list: A list of strings, where each string represents a separated 
              logical question chunk.
        """
        
        runnable = self.question_separation_prompt_template | self.model | self.json_parser
        chain = RunnableSequence(runnable)
        response = chain.invoke(questions)
        
        # Use this for only debugging purposes
        #parsed_response = self.json_parser.parse(response.content)
        #print("\nStep 3 - Parsed Response:")
        #print(parsed_response)
        return response
    
    def assign_correspondance_level(self, question:str):
        """
        Assigns a correspondence level to the given question by executing a sequence of operations.
        This method utilizes a predefined sequence of a prompt template, a model, and a JSON parser 
        to process the input question and generate a response. The sequence is executed using a 
        `RunnableSequence` object.
        Args:
            question (str): The input question for which the correspondence level is to be assigned.
        Returns:
            Any: The response generated by the sequence, which represents the assigned correspondence level.
        """        
        
        runnable = self.correspondance_assignment_prompt_template | self.model | self.json_parser
        chain = RunnableSequence(runnable)
        response = chain.invoke(question)
        
        return response    
    
    def summarize_conversation(self, conversation_history:dict):
        """
        Summarizes a conversation based on the provided conversation history.
        This method utilizes a sequence of runnable components, including a 
        summary prompt template, a model, and a JSON parser, to process the 
        conversation history and generate a summarized response.
        Args:
            conversation_history (dict): A dictionary containing the conversation 
                history to be summarized.
        Returns:
            dict: The summarized response generated by the chain.
        """
        
        runnable = self.summary_prompt_template | self.model | self.json_parser
        chain = RunnableSequence(runnable)
        response = chain.invoke(conversation_history)
        
        return response
    