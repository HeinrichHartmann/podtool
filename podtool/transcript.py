import openai
import logging

logger = logging.getLogger(__name__)

class Transcript:
    
    model: str = "gpt-4o-mini"
    
    def __init__(self, api_key):
        """Initialize the Transcript processor with OpenAI API key"""
        self.api_key = api_key
        openai.api_key = api_key

    def test_openai(self):
        response = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": "Hello, world!"}]
        )
        print(response)


    def refine(self, content : str):
        """
        Refine the transcript content using OpenAI's API
        
        Args:
            content (str): The raw transcript content
            
        Returns:
            str: The refined transcript content
        """
        assert(content is not None)
        
        # System message defining how to process the transcript
        system_message = {
            "role": "system",
            "content": """You process transcripts as follows:
            
            1. Fixing typos and correcting domain specific terms
            2. Keeping the language very close to the original
            3. Structure the raw input into paragraphs that are 2-5 sentences long
            4. Start each paragraph with a timestamp in the format [MM:SS]. Example "[12:23] The HDR histogram was..."
            5. DON'T include section headings in the transcript text"""
        }
        
        # Split content into manageable chunks
        lines = content.splitlines()
        chunk_size = 100
        chunks = [
            "\n".join(lines[i:i + chunk_size])
            for i in range(0, len(lines), chunk_size)
        ]
        
        processed_text = []
        last_message = []
        
        for chunk in chunks:
            if not chunk.strip():  # Skip empty chunks
                continue
            
            messages = [system_message, *last_message, {"role": "user", "content": chunk}]
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0,
            )

            chunk_content = response.choices[0].message.content
            last_message = [
                {"role": "user", "content": chunk},
                {"role": "assistant", "content": chunk_content}
            ]
            
            processed_text.append(chunk_content)
        
        return "\n".join(processed_text)
    
    
    def summarize(self, content: str):
        """
        Summarize the content of the transcript by breaking it into focused sub-tasks
        """

        logger.info("Creating title")
        title_prompt = """
        You are an expert podcast editor, analyzing a transcript from "CaSE – Conversations about Software Architecture".

        Based on the content, suggest 3 possible titles for the episode. Each title should be clear, engaging, and reflect 
        the main topic discussed. 
        Format your response as bullet point list.
        """
        titles_response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": title_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
        )
        
        logger.info("Creating teaser")
        teaser_prompt = """
        You are an expert podcast editor, analyzing a transcript from "CaSE – Conversations about Software Architecture".

        Create an engaging teaser paragraph for a software architecture podcast episode.
        Start with a thought-provoking question relevant to software architects and developers.
        The teaser should highlight the episode's core value proposition without marketing language.
        Keep it concise (2-3 sentences).
        """
        teaser_response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": teaser_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.4,
        )
        
        logger.info("Creating chapters")
        chapters_prompt = """
        You are an expert podcast editor, analyzing a transcript from "CaSE – Conversations about Software Architecture".

        Analyze this podcast transcript and break it into major thematic chapters.
        For each chapter:
        1. Create a clear heading
        2. Write a summary of the key points discussed
        3. Include one verbatim quote from the transcript that best represents the chapter
        4. Integrate relevant questions for software architects/developers
        
        Use clear technical language but avoid unnecessary complexity.
        Format each chapter with a heading followed by flowing text (avoid bullet points).
        Present quotes as separate paragraphs."""
        chapters_response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": chapters_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.2,
        )
        
        logger.info("Creating takeaways")
        takeaway_prompt = """
        You are an expert podcast editor, analyzing a transcript from "CaSE – Conversations about Software Architecture".

        Extract the 5-10 most relevant takeaways from the transcript, and present them as a list of bullet points.
        """
        takeaway_response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": takeaway_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.5,
        )
        
        logger.info("Creating shownotes")
        shownotes_prompt = """
        You are an expert podcast editor, analyzing a transcript from "CaSE – Conversations about Software Architecture".

        Extract a list of shownotes for the episode, i.e. references to the things that were mentioned.
        You don't need to include the links, just name relevant things that were mentioned.
        """
        shownotes_response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": shownotes_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.5,
        )
        
        return (
            f"# Title\n\n"
            f"{titles_response.choices[0].message.content}\n\n"
            f"# Teaser\n\n"
            f"{teaser_response.choices[0].message.content}\n\n"
            f"# Chapters\n\n"
            f"{chapters_response.choices[0].message.content}\n\n"
            f"# Takeaways\n\n"
            f"{takeaway_response.choices[0].message.content}\n\n"
            f"# Shownotes\n\n"
            f"{shownotes_response.choices[0].message.content}\n\n"
        )

    def critique(self, content):
        """
        Analyze the podcast transcript and provide detailed feedback for improvement.
        
        Args:
            content (str): The transcript content to analyze
            
        Returns:
            str: A detailed critique of the podcast including strengths, weaknesses, 
                 and specific suggestions for improvement
        """
        system_prompt = """You are an experienced podcast critic and coach. Analyze this podcast transcript 
        and provide detailed, constructive feedback. Focus on:
        1. Content quality and structure
        2. Speaking style and delivery
        3. Engagement and audience connection
        4. Technical aspects (pacing, clarity, etc.)
        5. Specific examples of what worked well
        6. Areas for improvement with actionable suggestions
        
        Conclude with a rating of the podcast on a scale of 1-10, where 1 is the worst and 10 is the best.
        
        Format your response with clear sections and concrete examples from the transcript."""

        user_prompt = f"Please analyze this podcast transcript and provide detailed feedback:\n\n{content}"
        
        critique_response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
        )
        
        return critique_response.choices[0].message.content
