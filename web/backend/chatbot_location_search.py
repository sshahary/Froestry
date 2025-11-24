from openai import OpenAI
import os
import requests
import time
import asyncio
import concurrent.futures
from pydantic import BaseModel, Field

class LocationInfo(BaseModel):
    summary: str
    latitude: float
    longitude: float

class ResponseStructure(BaseModel):
    summary_of_results: str
    locations: list[LocationInfo]
    tip: str

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

from locations import SortBy

class TreeLocationSearchConfig(BaseModel):
    location_name: str = Field(description='''Put here the naming of the place to search. It can be a concrete address, postal code, place coordinates or somethings else. If it's not specified, default to 'Heilbronn'.''')
    max_distance_to_search_km: float = Field(description='''Maximal distance from the place to search in kilometres. If the request is something general (i.e. 'What's the best tree to plant in Heilbronn'), than max distance should be as big as possible, so default to 50km. If the user specified that location should be nearby or other distance-related word, than use some common sense. I.e. if he's searching for trees near specific place, than distance should be rlatively small like 400 meters (0.4 km). If it's some postal code, than you can increase it to around 2km. In other cases, use some common sense.''')
    number_of_results: int = Field(description='''Number of places to search. If it's not specified, default to 10. If the user is asking just for the best tree, make the number of results 1.''', le=25)
    sort_by: SortBy = Field(description='''The way to sort the results before choosing the best number_of_results results. By default, filter results by final_score since they represent the best places to plant tree overall. If the user asked about the exact area to plant a tree (i.e. 'Can I plant a tree on this coordinates:?'), sort place by distance so that it finds the exact location user asked for.''')

def get_search_config(user_query: str) -> TreeLocationSearchConfig:

    system_prompt = '''You are an assistant to help people to find best places to plant trees. Based on the User Query, fill in the information that will be used to search best locations to plant trees later.'''
    full_user_prompt = f'''User Query: {user_query}'''
    response = client.responses.with_raw_response.parse(
        model="gpt-5",
        reasoning = {"effort": "minimal"},
        input=[
            {
            "role": "system",
            "content": [{
                "type": "input_text",
                "text": system_prompt,
            } ]
            },
            {
            "role": "user",
            "content": [{
                "type": "input_text",
                "text": full_user_prompt,
            } ]
            }
        ],
        text_format = TreeLocationSearchConfig
    )

    return response.parse().output_parsed

from locations import Location

def get_coordinates(place_naming: str) -> Location:
    full_user_prompt = f"""You are given a place (it can be either some concrete place / postal code / city etc).
    Search for coordinates of the given place and return them.
    If you cannot find the exact location, return the nearest one.
    Location: {place_naming}"""

    raw = client.responses.with_raw_response.parse(
        model="gpt-5",
        reasoning = {"effort": "low"},
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": full_user_prompt,
                    }
                ],
            }
        ],
        tools=[
            {"type": "web_search"}
        ],
        text_format=Location,
    )
 
    response = raw.parse()
    coords: Location = response.output_parsed

    return coords

from locations import get_result, SearchData, extract_useful_info


def sort_by_to_string(sort_by: SortBy) -> str | None:
    if sort_by == SortBy.DISTANCE:
        return "distance (starting from the closest) - distance from the given location"
    elif sort_by == SortBy.FINAL_SCORE:
        return "final score (starting from the highest) - score ranking best places to plant trees"
    elif sort_by == SortBy.HEAT_SCORE:
        return "heat score - score corresponding to the heat of the place (starting from the highest heat)"

# Moved Extraction class up to be used in write_nice_response
class Extraction(BaseModel):
    summary_of_results: str
    tip: str

def write_nice_response(user_query: str, search_config: TreeLocationSearchConfig, number_of_results: int) -> Extraction:
    sorting_string = f', sorted them by {sort_by_to_string(search_config.sort_by)} '
    
    # Prompt modified to ask for fields directly rather than a string with {{}}
    full_user_prompt = f'''You are a chat assistant to help people to find best places to plant trees. The user asked the following: "{user_query}". Before, you already searched for locations based on the user query. You searched for places near "{search_config.location_name}" within {search_config.max_distance_to_search_km} kilometers {sorting_string} and searched for maximum {search_config.number_of_results} results. In the response, you got {number_of_results} results.

Now, fill in the fields for the response:
1. summary_of_results: A short introduction sentence telling the user about the results found. Do not list the specific places in this summary, just introduce them.
2. tip: A helpful tip for the user about planting trees or their impact on ecology. If you cannot come up with a tip related to the user ask, provide some general tip. Make it engaging, e.g., 'Tip: Did you know that?', 'Tip: Ever wondered why?'.

Important: when writing the response, use only information that you have. Do not assume anything about how the system works. Do not hallucinate.

Examples:
summary_of_results: "Here are the best places to plant trees near TUM Campus Heilbronn:"
tip: "Did you know that planting trees can help to clean the air and reduce the noise level?"
------------
summary_of_results: "Info about placing a tree in the ~49.15° N, 9.22° E coordinates:"
tip: "Ever wondered why planting just one tree matters? It quietly cleans the air, cools the area, and stores carbon — all on its own."
'''
    response = client.responses.with_raw_response.parse(
        model="gpt-5",
        reasoning = {"effort": "minimal"},
        input=[
            {
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": full_user_prompt,
                }]
            }
        ],
        text_format=Extraction
    )
    return response.parse().output_parsed

def summarize_location_info(location_info: dict) -> str:
    query = f"""The user is considering placing a tree in the location. You are given a location info. Obviously we cannot give the user simple json file as response, so describe this information in user-friendly way. But still include all the necessary data.
    
    Location info: {location_info}.
    
    Make the summary relatively short."""
    response = client.responses.create(
        model="gpt-5",
        reasoning = {"effort": "low"},
        input=query,
    )
    return response.output_text


async def search_tree_locations(user_query: str) -> ResponseStructure:
    """Main function to search for tree locations based on user query"""
    
    # Step 1: Get search configuration from user query
    search_config = get_search_config(user_query)
    
    # Step 2: Get coordinates for the location
    location = get_coordinates(search_config.location_name)
    
    # Step 3: Create search data and get results
    search_data = SearchData(
        location=location, 
        sort_by=search_config.sort_by, 
        count_of_results=search_config.number_of_results, 
        radius_km=search_config.max_distance_to_search_km
    )
    
    results = get_result(search_data)
    number_of_results = len(results)
    
    # Step 4: Generate nice response (Extraction) directly
    # This combines the generation and extraction into one LLM call
    extraction_result = write_nice_response(user_query, search_config, number_of_results)
    
    # Step 5: Create LocationInfo objects for each result (parallel processing)
    async def process_location(result):
        useful_info = extract_useful_info(result)
        # Run the OpenAI API call in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            summary = await loop.run_in_executor(executor, summarize_location_info, useful_info)
        
        return LocationInfo(
            summary=summary,
            latitude=result['properties']['latitude'],
            longitude=result['properties']['longitude']
        )
    
    # Process all locations in parallel
    locations = await asyncio.gather(*[process_location(result) for result in results])
    
    # Step 6: Return ResponseStructure
    return ResponseStructure(
        summary_of_results=extraction_result.summary_of_results,
        locations=locations,
        tip=extraction_result.tip
    )

if __name__ == "__main__":
    async def main():
        user_query = "Is planting a tree directly in 42Heilbronn a good idea?"
        response = await search_tree_locations(user_query)
        import json
        print(json.dumps(response.dict(), indent=2, ensure_ascii=False))
    
    asyncio.run(main())
