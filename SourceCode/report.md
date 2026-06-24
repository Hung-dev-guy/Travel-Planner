\documentclass[a4paper, 12pt]{report}

% --- Các gói cần thiết (giữ nguyên như lần trước) ---
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{float}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{eso-pic}
\usepackage{tikz}
\usepackage{tabularx}
\usepackage{float}
\usetikzlibrary{calc}
\usepackage{tikzpagenodes}
\renewcommand{\contentsname}{Table of contents} 

% --- Lệnh vẽ khung (To hơn vùng soạn thảo) ---
\AddToShipoutPictureBG{%
  \AtPageLowerLeft{%
    \begin{tikzpicture}[remember picture, overlay]
      % Định nghĩa tọa độ mới bằng cách dịch chuyển các góc của vùng soạn thảo
      % Dịch trái 0.5cm, lên 0.5cm so với góc trên-trái
      \coordinate (TopLeft) at ($(current page text area.north west) + (-0.5cm, 0.5cm)$); 
      % Dịch phải 0.5cm, xuống 0.5cm so với góc dưới-phải
      \coordinate (BottomRight) at ($(current page text area.south east) + (0.5cm, -0.5cm)$); 
      % Vẽ hình chữ nhật dựa trên tọa độ mới
      \draw[line width=1pt] (TopLeft) rectangle (BottomRight); 
    \end{tikzpicture}%
  }%
}

\begin{document}

% --- Trang bìa ---
\begin{titlepage}
    \centering
    \thispagestyle{empty} % Quan trọng: không hiển thị header/footer/số trang tự động

    \vspace*{0.5cm}
    \large\textbf{POSTS AND TELECOMMUNICATIONS INSTITUTE OF TECHNOLOGY} \\ % Kiểm tra lại text này
    \textbf{FACULTY OF INFORMATION TECHNOLOGY 1} \\[2cm] % Kiểm tra lại text này

    % --- Logo (Đảm bảo file logo.png tồn tại) ---
    \includegraphics[width=0.25\textwidth]{Logos/Logo_PTIT_University.png} \\[2cm]

    % --- Tên môn học / Loại báo cáo / Tiêu đề (Kiểm tra lại text) ---
    \normalsize
    \textbf{INTERNSHIP } \\[0.5cm]
    \textbf{SEMESTER REPORT} \\[0.5cm]
    \Large\textbf{BUILDING TRAVEL PLANNER SUPPORT SYSTEM} \\[3cm]

    % --- Thông tin Giảng viên / Sinh viên (Kiểm tra lại text và căn chỉnh \hspace) ---
    \begin{flushleft}
    \hspace*{3.5cm} % Điều chỉnh giá trị này để căn lề trái của khối thông tin
    \normalsize
    \begin{tabular}{@{}ll}
        \textbf{Instructor:}    & Kim Ngoc Bach \\ [3pt]
        \textbf{Student:}     & Nguyen Manh Hung \\ [3pt]
        \textbf{Student ID:} & B23DCCE040 \\ [3pt]
        \textbf{Class ID:}           & D23CQCE04-B \\
    \end{tabular}
    \end{flushleft}

    \vfill 

    \vspace*{-5cm}
    \normalsize
    \textit{Hanoi} 

    \vspace*{5pt} 

\end{titlepage}

%---------------------new page--------------------------

\ClearShipoutPictureBG % <<< Đặt lệnh xóa viền ở ĐÂY, sau khi đã qua trang mục lục
% --- Trang Mục lục ---
%\pagenumbering{roman}  % Đặt số trang kiểu La Mã cho mục lục (i, ii, ...)
\tableofcontents       % Lệnh qu trọng: tạo và hiển thị mục lục ở đây

\chapter{Introduction To Project}
\section{Reasons to choose the topic}
Amidst the rapid digital transformation, the tourism industry is witnessing a significant increase in online platforms providing information and services. However, this development also brings with it many substantial challenges. One prominent issue is information overload: users have to access a huge amount of data from many different sources, some of which may be outdated, inaccurate, ambiguous, or inconsistent. Furthermore, content related to travel safety is often incomplete or difficult to verify; understanding of local culture is also not presented systematically, leading to the risk of misunderstanding or inappropriate behavior. Currently, although there are chatbots supporting tourism, most still fail to fully address the personalization issue, resulting in generic and in-depth consultation experiences. These limitations highlight the need to build an intelligent travel chatbot system capable of providing accurate, contextually relevant information and adapting to diverse user needs.

However, designing an effective travel chatbot is not simply about integrating a large language model (LLM), but also requires addressing many complex technical and system issues. First and foremost is the problem of ensuring information accuracy. Travel data changes constantly over time (ticket prices, opening hours, service policies), while data sources are inconsistent in structure and reliability. Using LLM also carries the risk of "hallucination," or the creation of content that appears plausible but is inaccurate. Furthermore, travel information often depends on specific conditions (time, target audience, budget), and if not handled carefully, it can lead to inaccuracies or misformatted presentations, causing misunderstandings for users.

Another significant challenge is handling ambiguous queries. Users often don't provide all the required information (e.g., time, budget, number of people), or use relative language like "cheap," "not too far," or "fairly quiet," making it difficult for the system to accurately interpret their desired level. Simultaneously, there's the personalization issue: users may not clearly define their needs, have conflicting preferences, or change priorities at different times. In the absence of historical data, providing appropriate suggestions becomes even more difficult. Conversely, excessive personalization without proper data control can compromise privacy or create an inflexible experience.

Beyond data-related issues and language understanding, the project also faces requirements for scalability, security, and multilingual support. As the number of users increases, the system needs to ensure stable performance and reasonable operating costs. At the same time, personal information such as itineraries, phone numbers, and trip details must be securely protected. In the international travel environment, multilingual support is crucial to ensure practical applicability. Finally, an equally important issue is system quality assessment: criteria and methods for measuring the accuracy, relevance, and personalization effectiveness of the chatbot need to be defined.
\section{Meaning of the project}
Based on the above analysis, the development of my travel planning support system project not only has practical significance in helping users access reliable and relevant information, but also possesses clear academic value. Specifically, as follows:
\subsection{Application}
Firstly, the system helps users reduce the time spent searching for and comparing travel information.
Reduces information overload from multiple sources, allowing users to focus on core, important information.
Provides clear information with specific terms and conditions.
Enhances personalized experiences, helping the system make decisions that better suit the user's individual needs.
For businesses:
Reduces customer service costs, automates 24/7 consultation.
Increases customer interaction, with chatbots capable of immediate responses.
Leverages existing user data to optimize personalization.
Beyond its benefits for users and businesses, the travel planning support system has high practical applicability in various deployment contexts.
First, the system can be directly integrated into the website or mobile application of travel businesses, hotels, travel agencies, or online booking platforms. With its 24/7 operation capability, chatbots can act as automated advisory assistants, helping customers look up information, suggest itineraries, and answer frequently asked questions without direct staff intervention. This helps businesses optimize resources, especially during peak travel seasons.

Secondly, the system can be scaled to serve various target groups such as domestic tourists, international tourists, or specialized groups (family tourism, adventure tourism, budget tourism, etc.). Thanks to its multilingual support and contextually personalized features, the system can adapt flexibly to the diverse needs of users in the global travel environment.

Thirdly, the system architecture is based on a hybrid model combining LLM and data retrieval mechanisms, allowing for easy data updating and expansion. When there are changes in ticket prices, policies, or destination information, the system can update the data source without retraining the entire model. This ensures sustainability and long-term maintainability.

Furthermore, the proposed model is not limited to the tourism sector but can also be extended to other service sectors such as education, healthcare, and e-commerce – sectors that also face challenges of information overload, personalization, and data reliability. Therefore, the project is not only locally applicable but also has the potential for reuse and scaling in various contexts.
\subsection{Academic}
Academically, the travel planning support system is not simply a chatbot application, but also an applied research project in the field of natural language processing and intelligent conversational systems.

Firstly, the project contributes to an in-depth analysis of the challenges in implementing large language models (LLMs) in a dynamic and highly context-dependent data environment. Unlike general text generation problems, the travel problem requires information to be accurate, up-to-date, and subject to specific conditions. Researching how to minimize hallucination through data retrieval mechanisms and information source control is a significant experimental contribution.

Secondly, the project provides a specific analytical framework for handling ambiguous queries in conversational systems. Issues such as the lack of required information, relative language, conflicting or changing preferences are common challenges that have not been fully addressed in many current chatbot systems. The design of the questioning mechanism to clarify and manage conversational state contributes to expanding research directions on more natural human-machine interaction.

Third, the project focuses on the problem of controlled personalization. Instead of absolute personalization, the system needs to balance recommendation efficiency with user privacy protection. This is a crucial issue in responsible AI research, especially in systems that collect and process personal data.

Fourth, the project proposes a method for evaluating the system not only based on automated metrics but also incorporating qualitative user evaluations. This helps clarify the gap between technical performance and real-world experience – a key concern in modern conversational system research.

Finally, the project can serve as an empirical reference for further research on LLM applications in the service sector. Analyzing the limitations, flaws, and areas for improvement of the system will provide a basis for future expanded research.

\chapter{Background Knowledge}
\section{LLM}
\subsection{Definition}
Large language models (LLMs) are a class of deep learning systems that are trained on vast datasets, enabling them to comprehend and produce natural language as well as various other forms of content across many different tasks. These models are based on a neural network architecture known as the transformer, which is particularly effective at processing word sequences and identifying patterns in textual data. [1].
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.2]{Diagrams/llm-architecture.jpg}
    \caption{Transformer - the base architecture for current LLMs}
\end{figure}
\subsection{Model Selection}
During the development of an agentic system, selecting the core language model plays a decisive role in determining the success or failure of the project, directly impacting performance, operational cost, and user experience (latency). The model selection process for Traplanner is evaluated based on the following stringent criteria:
\begin{itemize}
    \item \textbf{Reasoning and Planning Capability}: Traplanner involves complex itinerary generation, requiring the LLM to understand constraints such as time, geographical distance, and budget. The selected model must maintain logical consistency throughout multi-day planning processes.
    \item \textbf{Tool Calling / Function Calling Ability}: This is a fundamental requirement for an agent-based architecture. The model must be capable of producing structured function call requests (e.g., querying a MongoDB database and performing route search in Neo4j) in JSON format, and then incorporating the returned results to continue its reasoning process.
    \item \textbf{Context Window Size}: The system requires incorporating a massive amount of information into the prompt, including user preferences, hierarchical conversation history (memory), and detailed real-world travel location data (retrieved via \textbf{Graph RAG} from Polyglot databases). Therefore, the model must support a sufficiently large context window to prevent the loss of contextual information and grounding data during complex itinerary planning.
    \item \textbf{Trade-off Between Speed and Capability}: Instead of relying on heavy, costly, and slower models, Traplanner prioritizes lightweight and high-speed models (gemini-2.5-flash-lite and gemini-2.5-flash) as the default model. This choice aims to optimize real-time response latency for chatbot interactions while still maintaining adequate reasoning capabilities.
\end{itemize}

\subsection{Prompt Engineering}
To guide the LLM to function accurately as a domain-specific expert in the travel planning space, the Traplanner project employs prompt engineering techniques with a well-structured, hierarchical design
\begin{itemize}
    \item \textbf{System Prompt (Persona Definition \& Core Rules):} This serves as the foundational instruction set that defines the travel personal assistant, named TrapBot. The system prompt not only enforces a friendly and professional tone but also establishes strict guardrails, including rejecting out-of-scope queries, mandating structured output formats, and explicitly specifying when tool usage is required 
    \item \textbf{Dynamic Context Injection:} To effectively address the issue of hallucination, the system does not require users to repeatedly provide information. Instead, through the trip context template, all relevant real-world data—including trip ID, destinations, total budget, detailed daily itineraries, and summarized conversation history—is automatically injected into the prompt as structured data blocks. This approach forces the LLM to ground its reasoning in factual data rather than generating unsupported content.
\end{itemize}
\section{Multi-agent System}
\subsection{Definition}
A multi-agent system (MAS) is a computational framework composed of multiple interacting agents, where each agent operates autonomously with its own goals, perceptions, and decision-making capabilities. These agents collaborate, coordinate, or compete with one another to solve complex problems that are difficult or inefficient for a single agent to handle. By distributing tasks and enabling communication among agents, a multi-agent system can achieve greater scalability, flexibility, and robustness in dynamic and complex environments [2].
\subsection{Sequential Orchestration}
The sequential orchestration pattern organizes AI agents in a fixed, linear sequence, where each agent receives and processes the output produced by the previous one. This creates a pipeline in which tasks are handled through a series of specialized transformations [3].
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.2]{Diagrams/seqmas.png}
\end{figure}
This pattern, also referred to as a pipeline, prompt chaining, or linear delegation, is particularly suitable for problems that require step-by-step processing. Each stage incrementally refines the result, building upon earlier outputs to improve overall quality.

In the Traplanner project, this pattern is particularly well-suited for the core itinerary generation workflow. Producing a coherent and well-structured multi-day travel plan from a single user input is a highly complex task, as each stage of the process depends on the outputs generated in earlier stages.
\subsection{Polyglot Persistence}
A complex AI system such as Traplanner requires a diverse data storage architecture to support the varying analytical and retrieval needs of different agents. The adoption of a polyglot persistence architecture enables performance optimization by leveraging the most suitable type of database for each specific task [4]:

\begin{itemize}
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.1]{Logos/Gold_MongoDB_FG.jpg}
\end{figure}
\item \textbf{Document Database (MongoDB):} Serves as the ``source of truth'' for storing content and system state. MongoDB is particularly well-suited for handling the nested JSON structures of travel plans (Trips) and daily details (DayDetails), as well as static location information (e.g., name, description, images). Agents interact with MongoDB to efficiently read and write complete itinerary data.
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.3]{Logos/Neo4j-01.png}
\end{figure}
\item \textbf{Graph Database (Neo4j):} Plays a central role in solving spatial reasoning and routing problems. In Neo4j, locations are represented as nodes, while distances or travel times are modeled as edges. Instead of performing computationally expensive coordinate-based calculations in MongoDB, the \textit{Mobility Agent} leverages Neo4j to execute high-performance graph queries for clustering nearby locations into the same day or determining optimal travel routes between activities.
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.2]{Logos/redis.png}
\end{figure}
\item \textbf{In-memory Store (Redis):} Provides ultra-fast read/write operations (millisecond-level latency), making it ideal for storing the chatbot’s short-term contextual memory. This allows the system to respond to follow-up user queries in real time without overloading the primary databases.


\end{itemize}
\section{RAG} 
 RAG (Retrieval Augmented Generation) is an architecture enhancing generative AI systems by enabling them to retrieve information from external knowledge sources, including organizational databases, academic publications, and domain-specific datasets. By incorporating this retrieved context into the response generation process, chatbots and other NLP applications can produce more accurate and specialized outputs without requiring additional model retraining.
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/rag.jpg}
    \caption{Basic architecture of RAG.}
\end{figure}

\section{AgenticRAG}
\subsection{Definition}
Agentic RAG extends traditional RAG architectures by integrating autonomous agents capable of planning, decision-making, and adaptive retrieval. Rather than relying on a fixed retrieval-generation pipeline, it iteratively refines its actions and retrieval strategies based on task requirements, making it well-suited for complex and dynamic information-seeking scenarios. This approach preserves the modularity of RAG while adding a layer of intelligent agent-based control. [5].

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/agentic-rag.jpg}
    \caption{Basic architecture of Agentic RAG.}
\end{figure}

\subsection{ReAct}
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/reAct.png}
    \caption{Basic architecture of reAct.}
\end{figure}

ReAct is a pioneering framework that maximizes the capabilities of large language models (LLMs) by tightly integrating \textbf{Reasoning} and \textbf{Acting} [6]. In theory, a ReAct cycle consists of three continuously interleaved steps:

\begin{itemize}
\item \textbf{Thought (Reasoning):} The LLM generates intermediate "thoughts" to analyze the problem, formulate plans, or guide the next step. Unlike Chain-of-Thought techniques (which focus solely on internal reasoning), ReAct enables reasoning that explicitly drives interaction with the external environment.

\item \textbf{Action (Acting):} Based on its reasoning, the LLM decides to interact with the external world by invoking tools, APIs, or querying databases.

\item \textbf{Observation (Observation):} The LLM receives real-world results from the executed action and incorporates them as context for subsequent reasoning steps.


\end{itemize}

This continuous interleaving process (Thought $\rightarrow$ Action $\rightarrow$ Observation) mitigates the hallucination problem in LLMs in Traplanner project, as each reasoning step is grounded in real data obtained during execution.

\subsection{Hierarchical Memory Management}
\textbf{Hierarchical Memory Management} is a multi-layered memory architecture in which information is categorized, stored, and retrieved based on its level of granularity, abstraction, and temporal persistence. According to [7], this architecture is designed to address a fundamental limitation of modern AI systems: feeding the entire raw interaction history into the model can overload the context window, increase latency, and degrade the model's ability to focus during long task sequences.

Building upon the principles of G-Memory, the Traplanner project implements a hierarchical memory system by separating information flow into two specialized storage layers:

\begin{itemize}
\item \textbf{Fine-grained Interaction Trajectories (Short-term Memory):} This layer stores a precise, verbatim record of the most recent messages (e.g., the last 10--30 turns) in a high-speed in-memory store (e.g., Redis). It provides the agent with immediate conversational context, ensuring continuity of the dialogue flow without interference from outdated topics.

\item \textbf{High-level Generalizable Insights (Long-term Memory \& Summarization):} To capture cross-session knowledge, the system leverages the LLM itself to extract and condense key insights from past interactions (e.g., dietary preferences, budget constraints, travel habits). These summaries function as a persistent user profile. When initializing, the agent retrieves only these high-level insights instead of reprocessing extensive raw conversation logs, thereby enabling personalization while optimizing token usage and computational efficiency.


\end{itemize}

\chapter{System Description}
\section{Overview}
Traplanner is an intelligent travel planning and consultation platform that leverages Agentic AI and Multi-Agent System architectures. Instead of requiring users to manually search for destinations, estimate travel time, and organize itineraries, Traplanner automates the entire process.

The system allows users to input travel requests in natural language. Based on this input, the AI system automatically extracts constraints, performs reasoning, clusters locations, optimizes routes, and generates a detailed day-by-day itinerary.

Additionally, the platform provides a dedicated virtual assistant, enabling users to interact conversationally, refine itineraries, and ask for travel-related information in real time.

\section{Survey of Similar Systems}

To establish a solid foundation for the system design process, I have conducted an analysis of several widely used travel planning platforms and applications to derive practical insights and identify existing limitations.

\begin{table}[H]
\centering
\renewcommand{\arraystretch}{1.5}

\begin{tabularx}{\textwidth}{|p{3cm}|X|X|X|}
\hline
\textbf{System} & \textbf{Description} & \textbf{Strengths} & \textbf{Limitations} \\
\hline

\textbf{Tripadvisor / Expedia Trip Planner}
&
Global travel planning and online booking platforms.
&
Possess extensive databases of destination reviews, user-friendly interfaces, and recommendations for popular and reliable attractions.
&
Generated itineraries tend to be generic, lacking deep personalization. Their workflows are relatively rigid and offer limited flexibility for detailed hourly customization.
\\
\hline

\textbf{Wanderlog}
&
A dedicated travel planning application featuring interactive maps.
&
Provides an intuitive drag-and-drop interface, excellent map integration, collaborative trip planning, and convenient expense tracking.
&
Requires users to manually construct most of their itineraries. AI-powered recommendation features remain limited and do not automatically optimize travel routes.
\\
\hline

\textbf{ChatGPT and other LLMs}
&
General-purpose conversational AI assistants powered by Large Language Models (LLMs).
&
Capable of generating travel itineraries quickly through natural language interactions, understanding complex contexts, and providing flexible responses.
&
Prone to data hallucinations (e.g., suggesting non-existent hotels, restaurants, or prices), lacks accurate geographical route optimization capabilities due to the absence of graph-based spatial reasoning, and does not provide a visual destination management interface (UI Cards).
\\
\hline

\end{tabularx}

\caption{Comparison of Existing Travel Planning Systems}
\label{tab:similar_systems}
\end{table}

Based on the survey results, the proposed \textbf{Traplanner} system is designed around several key user-centric objectives. The platform serves as an intelligent travel assistant capable of automatically generating fully personalized itineraries based on verified real-world destination data. The system prioritizes logical route planning to minimize travel times and optimize the daily schedule. Furthermore, Traplanner provides a flexible interaction model that combines a conversational chatbot with an intuitive dashboard, allowing users to make real-time adjustments to their itineraries and effectively overcoming the rigid limitations of existing travel solutions.

\chapter{System Requirements}
\section{Terminologies} 
\begin{table}[H]
\centering
\renewcommand{\arraystretch}{1.5}
\begin{tabularx}{\textwidth}{|c|p{4.5cm}|X|}
\hline
\textbf{No} & \textbf{Terminology} & \textbf{Description} \\
\hline
1 & Itinerary & A detailed plan for a journey, including a sequence of planned activities, destinations to visit, and their respective time-slots. \\
\hline
2 & Destination & A geographical location or specific region that a traveler plans to visit during their trip. \\
\hline
3 & Point of Interest (POI) & A specific physical location, attraction, or landmark that is considered useful or interesting for a tourist to visit. \\
\hline
4 & Accommodation & A lodging place such as a hotel, resort, or homestay where a traveler stays overnight during the trip. \\
\hline
5 & Activity & A specific experiential event, tour, or recreational action scheduled within the travel itinerary. \\
\hline
6 & Transit / Mobility & The process, duration, or means of transportation used to travel between different points of interest or accommodations. \\
\hline
7 & Time-slot & A designated, bounded period of time allocated for a specific activity or transit within the daily schedule. \\
\hline
8 & Travel Preference & The specific constraints, requirements, or personal desires of the traveler, such as budget limits, travel pace, or dietary needs. \\
\hline
9 & Booking / Reservation & An arrangement made in advance to secure a service, such as a hotel room, restaurant table, or tour ticket. \\
\hline
10 & Check-in / Check-out & The formal administrative process of arriving to register at, or departing to settle bills from, an accommodation. \\
\hline
\end{tabularx}
\end{table}
\section{Business Model in Natural Language}
\subsection{Targets and Boundary of System}
\begin{itemize}
\item \textbf{Targets:}
\begin{itemize}
    \item Build an intelligent, automated travel planning system leveraging Agentic AI and Multi-Agent System to assist tourists in creating highly personalized travel itineraries effortlessly.
    \item Automate core travel planning processes including: user preference extraction, destination matching, logical travel route and finance optimization, and detailed time-slot scheduling.
    \item Ensure data integrity and geographical accuracy by utilizing a Polyglot Persistence architecture (combining MongoDB and Neo4j), strictly preventing AI hallucinations regarding real-world locations and service costs.
\end{itemize}

\item \textbf{Boundary:}
\begin{itemize}
    \item \textbf{Geospatial Data Management:} Allow administrators to add, modify, delete, and search for real-world tourist attractions, accommodations, and dining establishments within the target region.
    \item \textbf{Intelligent Itinerary Generation:} Provide a conversational chatbot interface to accurately capture user constraints (budget, duration, pace, ...) and dynamically generate complete multi-day travel plans.
    \item \textbf{Itinerary Customization \& Visualization:} Enable users to view detailed day-by-day schedules, edit or replace specific activities, and visualize travel routes interactively.
    \item \textbf{User History \& Dashboard:} Allow users to manage their profiles, review past generated trips, and access personal travel statistics on a centralized dashboard.
\end{itemize}
\end{itemize}
The system involves two main user groups (actors):

\begin{table}[H]
\centering
\renewcommand{\arraystretch}{1.5}
\begin{tabularx}{\textwidth}{|c|p{4.5cm}|X|}
\hline
\textbf{Actor} & \textbf{Description} & \textbf{Main Role} \\
\hline
\textbf{Tourist (User)} & The end-user who directly interacts with the AI assistant to plan their personal trips. & Interacts with the chatbot, generates and customizes itineraries, views maps, and manages personal travel history. \\
\hline
\textbf{Administrator} & The operator responsible for maintaining the system's data foundation and overall platform operations. & Manages the database of destinations and accommodations, ensures data integrity, and monitors system workflows. \\
\hline
\end{tabularx}
\end{table}

\subsection{Users Functions}
\begin{itemize}
    
\item \textbf{Administrator:}
\begin{itemize}
    \item \textbf{Geospatial Data Management:} Create new, search, and update information regarding tourist destinations, accommodations, and dining locations within the system (synchronizing across MongoDB and Neo4j).
    \item \textbf{System Statistics Management:} Monitor overall system usage, including the number of generated itineraries, most frequently suggested destinations, and active user metrics.
\end{itemize}

\item \textbf{Tourist (User):}
\begin{itemize}
    \item \textbf{Itinerary Generation Management:} Interact with the AI chatbot, provide travel preferences (travel dates, budget, pace, interests), and receive a dynamically generated multi-day travel schedule.
    \item \textbf{Itinerary Customization Management:} View the detailed day-by-day itinerary, visualize travel routes on a map, and perform interactive modifications (such as replacing specific activities or accommodations).
    \item \textbf{Travel History Management:} Access the personal dashboard to view recently generated trips, review detailed past itineraries, and delete unwanted trip records.
\end{itemize}

\end{itemize}
\subsection{Functions Information}

\begin{itemize}
    \item \textbf{Geospatial Data Management:} The administrator accesses the data management portal. To update a location, the admin inputs the destination name into the search bar, and the system displays matching results. Upon selecting a specific location, the interface shows current details (name, description, coordinates, image URL, pricing). The admin edits the necessary fields and confirms the update. The system automatically synchronizes these changes across the Polyglot Persistence databases (MongoDB and Neo4j) and displays a success notification.
    
    \item \textbf{Itinerary Generation:} The user initiates a conversation via the AI Chatbot interface. The user provides natural language inputs regarding their travel requirements. The system's Agentic Workflow processes this request through its specialized nodes (Extractor, Planner, Mobility, Scheduler, Validation). Once validated, the system presents a comprehensive, logically sequenced day-by-day itinerary, complete with designated time-slots and transportation details.
    
    \item \textbf{Itinerary Customization:} The user accesses the detailed view of a generated itinerary. If they wish to change a specific activity or hotel, they click the edit/replace button for that item. The system queries the Knowledge Graph to suggest suitable alternatives based on spatial proximity, user budget, and category tags. Upon selecting an alternative, the system automatically recalculates the transit times, updates the daily timeline, and saves the modified itinerary.
    
    \item \textbf{Travel Statistics Management:} The user navigates to their personal Dashboard page. The interface displays a summary of their travel statistics alongside a list of recently generated trips (showing basic info like trip title, dates, and total estimated cost). The user can click on any trip card to view the full itinerary details or select the delete option to permanently remove the trip record from their account history.
\end{itemize}
\subsection{Objects need Processing}

\begin{itemize}
    \item \textbf{User (Tourist):} User ID, Username, Email, Password (hashed), Created At.
    \item \textbf{Location:} Location ID, Name, Category (Stay, Food, Sightseeing, Culture), Address (Ward Name, Province Name), Description, Estimated Price, Estimated Duration, Suitability For, Image URL. 
    \item \textbf{Trip:} Trip ID, Linked User ID, Destination, Total Budget, Status, Created At.
    \item \textbf{Day Detail:} Day Schedule Detailed ID, Linked Trip ID, Day Number.
    \item \textbf{Activity:} Activity Name, Start Time, End Time, Estimated Cost, Description, Note.
    \item \textbf{Geospatial Node:} Node Name, Node Type (Province, Ward).
    \item \textbf{Transportation:} From City, To City, Transport Type, Provider, Duration Hours, Price, Departure Times.
    \item \textbf{Chat Memory (Session):} Session ID, Linked User ID, Message Context, Timestamp.
\end{itemize}

\subsection{Relationships between objects}

\begin{itemize}
    \item \textbf{User and Trip (1-N):} A user can create and own multiple travel trips over time; each trip document in MongoDB is linked to exactly one user.
    \item \textbf{Trip and Day Detail (1-N):} A multi-day trip is composed of several consecutive day schedules; each day schedule is bound exclusively to one specific trip.
    \item \textbf{Day Detail and Activity (1-N):} A single day schedule document contains an embedded array of chronological activities; each activity is scheduled within exactly one trip day.
    \item \textbf{Activity and Location (N-1):} Many activities across different users' itineraries can reference the same Location entity (Stay/Restaurant/Attraction) from the database.
    \item \textbf{Province and Ward (1-N):} a Province node has multiple wards, a ward belongs to one province.
    \item \textbf{Ward and Ward (N-N):} Ward nodes are spatially connected to each other to facilitate geographical proximity queries.
    \item \textbf{User and Chat Memory (1-N):} A user can interact in multiple separate conversation sessions with the AI chatbot; each chat session's context is tied to exactly one user.
\end{itemize}


\subsection{Business model by UML}

\subsubsection{Actor List}

\begin{table}[H]
\centering
\renewcommand{\arraystretch}{1.5}
\begin{tabularx}{\textwidth}{|c|p{3.5cm}|X|}
\hline
\textbf{No} & \textbf{Actor} & \textbf{Detailed Description} \\
\hline
1 & Tourist (User) & The primary end-user of the system. Directly interacts with the AI chatbot to generate personalized itineraries, customizes travel plans, and manages their personal travel history. \\
\hline
2 & Administrator & Responsible for the system's business operations and data foundation, manages geospatial information and monitors system-wide statistics. \\
\hline
\end{tabularx}
\end{table}

\subsubsection{General Use Case Diagram}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/general_usecase.png}
\end{figure}

The primary use cases are described as follows:

\begin{itemize}
    \item \textbf{Geospatial Data Management:} This use case allows the administrator to add, edit, and delete detailed information regarding tourist destinations, accommodations, and restaurants within the centralized Polyglot database.
    
    \item \textbf{Intelligent Itinerary Generation:} This use case allows the tourist to interact with the conversational AI chatbot, provide personal travel constraints (budget, time, interests), and receive a fully automated, logically sequenced multi-day travel schedule.
    
    \item \textbf{Itinerary Customization:} This use case allows the tourist to view their generated schedule in detail, interactively replace specific activities or hotels with system-suggested alternatives, and visualize the travel route on a map.
    
    \item \textbf{Travel History Management:} This use case allows the tourist to access their personal dashboard to review a list of past generated trips, open detailed past itineraries, and delete unwanted trip records.
\end{itemize}

\chapter{Analysis}

\section{Description}
The Traplanner system manages real-world travel locations, itineraries, user preferences, and chatbot interactions. The system allows administrators to manage and update geospatial data such as tourist destinations, accommodations, and restaurants. Users log into the system to interact with trip planner, which generates personalized travel schedules based on their constraints (budget, time, ...). Users can view their generated itineraries (trip) in detail, they can also replace detail of the itinerary. During the generation process, the system creates trips, assigns consecutive Day Details, and schedules multiple Activities that are linked to specific Locations. The system also leverages a knowledge graph consisting of provinces and wards to optimize geographical routing and proximity. Finally, the system allows users to manage their personal travel history via a dashboard, while administrators can monitor system-wide statistics.

\sectionsection{Nouns Extraction}
\begin{itemize}
    \item System, information, preferences, results, lists, statistics, constraints: General nouns $\rightarrow$ Types.
    \item User: Represents the individual account logging into the system $\rightarrow$ Entity class: \textbf{User}.
    \item Administrator: The user responsible for managing the system's geospatial data and monitoring statistics $\rightarrow$ Entity class: \textbf{Administrator} (inherits from User).
    \item Tourist: The primary end-user interacting with the chatbot to plan trips $\rightarrow$ Entity class: \textbf{Tourist} (inherits from User).
    \item Location: The physical place (Accommodation, Restaurant, Attraction) managed in the database $\rightarrow$ Entity class: \textbf{Location}.
    \item Trip: The main travel plan entity generated for the user $\rightarrow$ Entity class: \textbf{Trip}.
    \item Day Detail: A specific day's schedule within a multi-day trip $\rightarrow$ Entity class: \textbf{DayDetail}.
    \item Activity: A specific event or action scheduled within a Day Detail, linked to a Location $\rightarrow$ Entity class: \textbf{Activity}.
    \item Province: A high-level geospatial administrative node $\rightarrow$ Entity class: \textbf{Province}.
    \item Ward: A lower-level geospatial node belonging to a Province $\rightarrow$ Entity class: \textbf{Ward}.
    \item Transportation: The record of travel mode and duration between cities $\rightarrow$ Entity class: \textbf{Transportation}.
    \item Chat Memory: The recorded context and conversation history of a user's chatbot session $\rightarrow$ Entity class: \textbf{ChatMemory}.
    \item User ID, Username, Description, Estimated Price, Start Time, End Time: Abstract details $\rightarrow$ Types 
\end{itemize}
\textbf{Final list of entity classes:} User, Administrator, Tourist, Location, Trip, DayDetail, Activity, Province, Ward, Transportation, ChatMemory.

\section{Relationships among Entities}
\begin{itemize}
    \item \textbf{User, Administrator, Tourist (Inheritance):} Administrator and Tourist are derived from the base User class, sharing common authentication attributes.
    \item \textbf{User and Trip (1-N):} A user can create and own multiple travel trips over time; each trip document is linked to exactly one user.
    \item \textbf{Trip and DayDetail (1-N):} A multi-day trip is composed of several consecutive day schedules; each DayDetail is bound exclusively to one specific trip.
    \item \textbf{DayDetail and Activity (1-N):} A single day schedule contains a chronological sequence of multiple activities; each activity is scheduled within exactly one DayDetail.
    \item \textbf{Activity and Location (N-1):} Many activities across different users' itineraries can reference the same Location entity from the database; a specific activity occurs at exactly one Location.
    \item \textbf{Province and Ward (1-N):} A Province node hierarchically contains multiple Ward nodes; a Ward node belongs to exactly one Province.
    \item \textbf{Ward and Ward (N-N):} Ward nodes are spatially connected to each other to facilitate geographical proximity queries for the AI routing.
    \item \textbf{User and ChatMemory (1-N):} A user can interact in multiple separate conversation sessions with the AI chatbot; each chat session's memory is tied to exactly one user.
\end{itemize}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/ERD_analysis_phase.png}
    \caption{Entities relationship diagram}
\end{figure}

\section{Scenarios}
\subsection{Scenario of User Planning a Trip}

\textbf{Main flow:}
\begin{enumerate}
\item The user accesses the system to plan a new trip.
\item The system displays the main interface with a trip information input form.
\item The user enters information including: destination (e.g., Hanoi, Ninh Binh), number of days, estimated budget, number of people, and travel preferences.
\item The user clicks the ``Generate Itinerary'' button.
\item The system receives the request and sends the data to the Multi-Agent Pipeline.
\item The Extractor Agent extracts relevant information from the input data.
\item The Planner Agent searches for geographical areas in Neo4j and specific locations (hotels, attractions) in the MongoDB database to create a high-level itinerary framework.
\item The Mobility Agent determines suitable transportation options between locations using the Neo4j spatial graph.
\item The Scheduler Agent allocates specific time slots (start time, end time) for each activity during the day.
\item The Validation Agent checks the overall feasibility of the itinerary.
\item After processing is complete, the system stores all trip information and itinerary details in the MongoDB database.
\item The system displays a detailed itinerary interface with a list of activities for each day.
\end{enumerate}

\textbf{Exception flow:}
\begin{enumerate}
\item[3.]
\begin{enumerate}
\item[3.1.] If the user does not provide all required fields (such as destination or number of days), the system displays a warning: ``Please fill in all required information'' and prevents form submission.
\end{enumerate}

\item[10.]
\begin{enumerate}
    \item[10.1.] If the Validation Agent detects that the itinerary is not feasible (e.g., travel time is too tight, budget is exceeded), the system requests the Scheduler and Planner Agents to adjust the plan. If it still fails after multiple attempts, the system displays: ``Unable to generate an itinerary with the current requirements. Please adjust your input.'' and returns to the input form.
\end{enumerate}

\end{enumerate}

\subsection{Scenario of User Interacting with Chatbot and Modifying the Trip Plan}

\textbf{Main flow:}
\begin{enumerate}
\item The user is viewing a detailed itinerary and wants to modify an activity (e.g., change a hotel or add a dining location).
\item The user opens the Chatbot interface integrated into the itinerary screen.
\item The user enters a request message. Example: ``Change the hotel in Ninh Binh to a cheaper one, under 500k''.
\item The user clicks the send button.
\item The system (ReAct Agent) receives the message, retrieves chat history (Hierarchical Memory), and the current trip context from MongoDB.
\item The system analyzes the intent and decides to call an appropriate tool (querying MongoDB for locations or Neo4j for transportation) with necessary parameters.
\item The system receives results from the database and returns a list of suitable options to the user via the chat interface.
\item The user selects a specific option from the list.
\item The system confirms the selection and updates the new activity into a day of the trip in MongoDB.
\item The system sends a confirmation message indicating the update was successful.
\item The frontend itinerary interface automatically reloads to display the updated data.
\end{enumerate}

\textbf{Exception flow:}
\begin{enumerate}
\item[7.]
\begin{enumerate}
\item[7.1.] If the system cannot find any results in the database that match the user's conditions, it responds via Chatbot: ``Sorry, I couldn't find any suitable results. Would you like to modify your request?''.
\end{enumerate}

\item[9.]
\begin{enumerate}
    \item[9.1.] If an error occurs while saving updates to MongoDB, the system responds via Chatbot: ``An error occurred while updating the itinerary. Please try again later.''.
\end{enumerate}


\end{enumerate}

\section{Detailed Analysis of Each Module}
\subsection{User generates trip}
\subsection{Detailed Analysis of User Generate Trip Module}

The tourist accesses the system through the \textbf{ChatbotPage} component, which allows users to enter trip requirements such as budget constraints, time constraints, preferred destinations, and travel preferences.

After the user submits the request, the system performs the following process:

\begin{enumerate}
    \item The system receives and analyzes the user's request by invoking the \textbf{extractor\_node()} function, which belongs to the \textbf{Workflow Agent}.
    
    \item After extracting and structuring the trip requirements, the system initializes a new trip and stores its information using the \textbf{save\_full\_trip()} function, which belongs to the \textbf{Database Handler}.
    
    \item The system generates a detailed itinerary for each day of the trip by invoking the \textbf{scheduler\_node()} function, which belongs to the \textbf{Workflow Agent}.
    
    \item During itinerary generation, the scheduler searches for suitable accommodations, restaurants, and attractions from the knowledge graph by calling the \textbf{fetch\_locations\_from\_mongo()} function, which belongs to the \textbf{Location Handler}.
    
    \item After the itinerary has been successfully generated, the system returns a success notification to the user.
    
    \item The user can view the generated trip through the proposed \textbf{TripDayDetailPage} component. This page displays the complete itinerary, including trip days and detailed activities.
    
    \item To retrieve trip information, the system invokes the \textbf{get\_full\_trip\_context()} function, which belongs to the \textbf{Database Handler}.
    
    \item The user may update or replace an activity within the itinerary. This operation is performed through the \textbf{update\_activity\_in\_day()} function, which belongs to the \textbf{Database Handler}.
\end{enumerate}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/analysis_phase_erd_gen_trip.png}
    \caption{Functional Analysis Class Diagram}
\end{figure}


\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/analysis_phase_seq_gen_trip.png}
    \caption{Functional Analysis Sequence Diagram}
\end{figure}

The sequence of interactions for the User Generate Trip module is described as follows:

\begin{enumerate}
    \item The user enters trip requirements in the \textbf{ChatbotPage} and clicks the \textbf{Send} button.
    
    \item The \textbf{ChatbotPage} forwards the request to the \textbf{Workflow Agent}.
    
    \item The \textbf{Workflow Agent} invokes the \textbf{extractor\_node()} function to analyze and extract trip requirements.
    
    \item The \textbf{Workflow Agent} invokes the \textbf{planner\_node()} function to generate the overall trip plan.
    
    \item The \textbf{Workflow Agent} calls the \textbf{save\_full\_trip()} function to store the trip, trip days, and activities.
    
    \item The \textbf{Workflow Agent} invokes the \textbf{scheduler\_node()} function to generate detailed daily schedules.
    
    \item The \textbf{scheduler\_node()} function calls \textbf{fetch\_locations\_from\_mongo()} to retrieve accommodation, restaurant, and attraction information.
    
    \item The location database returns the relevant location data to the \textbf{Workflow Agent}.
    
    \item The \textbf{Workflow Agent} returns a successful trip generation result to the \textbf{ChatbotPage}.
    
    \item The \textbf{ChatbotPage} displays a completion message and provides a link to view the generated trip.
    
    \item The user clicks the link to view trip details.
    
    \item The system navigates the user from the \textbf{ChatbotPage} to the \textbf{TripDayDetailPage}.
    
    \item The \textbf{TripDayDetailPage} sends a request to the API to retrieve trip information.
    
    \item The API invokes the \textbf{get\_full\_trip\_context()} function.
    
    \item The \textbf{get\_full\_trip\_context()} function returns the complete trip data to the API, which then forwards it to the \textbf{TripDayDetailPage}.
    
    \item The \textbf{TripDayDetailPage} displays the generated itinerary to the user.
    
    \item The user selects an activity to update.
    
    \item The \textbf{TripDayDetailPage} sends an update request to the API.
    
    \item The API invokes the \textbf{update\_activity\_in\_day()} function.
    
    \item The \textbf{update\_activity\_in\_day()} function updates the activity and returns the result.
    
    \item The \textbf{TripDayDetailPage} displays a success notification and refreshes the itinerary view.
\end{enumerate}

\subsection{Detailed Analysis of User using chatbot Module}

The tourist accesses the system through the \textbf{ChatbotPage} component, which provides a conversational interface for interacting with the AI assistant.

After the user enters a message and clicks the \textbf{Send} button, the system performs the following process:

\begin{enumerate}
    \item The \textbf{ChatbotPage} sends the user's message to the backend through the \textbf{chat()} function, which belongs to the \textbf{API Routing} handler.
    
    \item Before processing the new message, the system retrieves the user's recent conversation history by invoking the \textbf{load\_short\_term\_memory()} function, which belongs to the \textbf{Memory Manager}.
    
    \item The system passes the user's message together with the retrieved conversation context to the AI agent through the \textbf{invoke()} function, which belongs to the \textbf{Workflow Agent}.
    
    \item During response generation, if the user requests information related to an existing trip, the AI agent retrieves the corresponding trip details by calling the \textbf{get\_full\_trip\_context()} function, which belongs to the \textbf{Database Handler}.
    
    \item After the response has been generated, the system stores both the user's message and the AI-generated response by invoking the \textbf{save\_short\_term\_memory()} function, which belongs to the \textbf{Memory Manager}.
    
    \item Finally, the system returns the response payload to the \textbf{ChatbotPage}, which updates the user interface and displays the conversation to the user.
\end{enumerate}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/analysis_phase_erd_chatbot.png}
    \caption{Functional Analysis Class Diagram}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/analysis_phase_seq_chatbot.png}
    \caption{Functional Analysis Sequence Diagram}
\end{figure}


The sequence of interactions for the Chat Module is described as follows:

\begin{enumerate}
    \item The user enters a message in the \textbf{ChatbotPage} and clicks the \textbf{Send} button.
    
    \item The \textbf{ChatbotPage} sends the request to the \textbf{API Routing} component for processing.
    
    \item The \textbf{API Routing} component invokes the \textbf{load\_short\_term\_memory()} function to retrieve the user's recent conversation history.
    
    \item The \textbf{Memory Manager} returns the conversation history to the \textbf{API Routing} component.
    
    \item The \textbf{API Routing} component invokes the \textbf{invoke()} function of the \textbf{Workflow Agent}, passing the user's message and conversation history.
    
    \item The \textbf{Workflow Agent} analyzes the user's intent and determines whether additional trip context is required.
    
    \item If necessary, the \textbf{Workflow Agent} invokes the \textbf{get\_full\_trip\_context()} function.
    
    \item The \textbf{Database Handler} returns the requested trip data to the \textbf{Workflow Agent}.
    
    \item The \textbf{Workflow Agent} generates the final response and returns it to the \textbf{API Routing} component.
    
    \item The \textbf{API Routing} component invokes the \textbf{save\_short\_term\_memory()} function to store the new conversation turn.
    
    \item The \textbf{Memory Manager} saves the conversation data and returns a confirmation to the \textbf{API Routing} component.
    
    \item The \textbf{API Routing} component returns the final response payload to the \textbf{ChatbotPage}.
    
    \item The \textbf{ChatbotPage} displays the AI-generated response to the user.
\end{enumerate}

\subsection{Detailed Analysis of User views trip statistics Module}

The tourist accesses the system through the \textbf{DashboardPage} component, which provides an overview of personal travel history, statistics, and trip-related insights.

When the page is loaded, the system performs the following process:

\begin{enumerate}
    \item The \textbf{DashboardPage} requests the user's dashboard data by invoking the \textbf{getStats()} function, which belongs to the \textbf{dashboardService} handler.
    
    \item The \textbf{dashboardService} forwards the request to the backend through the \textbf{dashboard\_stats()} function, which belongs to the \textbf{API Routing} handler.
    
    \item To generate the dashboard statistics, the backend retrieves all trips and trip-day details associated with the user by invoking the \textbf{find()} function, which belongs to the \textbf{Database Handler}.
    
    \item The system aggregates the retrieved data and calculates various statistics, including:
    \begin{itemize}
        \item Total number of trips,
        \item Budget and spending trends,
        \item Monthly travel activity distributions,
        \item Other travel-related insights.
    \end{itemize}
    
    \item If the user has no travel history, the system retrieves and displays a predefined set of demo trips as fallback data.
    
    \item After completing the calculations, the system returns the aggregated statistics and cost distribution data as a JSON payload to the \textbf{DashboardPage}.
    
    \item Finally, the \textbf{DashboardPage} renders the charts, summary cards, and recent trip list for the user.
\end{enumerate}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/analysis_phase_erd_view_stats.png}
    \caption{Functional Analysis Class Diagram}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/analysis_phase_seq_view_stats.png}
    \caption{Functional Analysis Sequence Diagram}
\end{figure}

The sequence of interactions for the Dashboard Statistics Module is described as follows:

\begin{enumerate}
    \item The user accesses the \textbf{DashboardPage}.
    
    \item The \textbf{DashboardPage} invokes the \textbf{dashboardService} to retrieve dashboard statistics.
    
    \item The \textbf{dashboardService} sends a request to the corresponding \textbf{GET API} endpoint.
    
    \item The \textbf{API Routing} component invokes the \textbf{dashboard\_stats()} function to process the request.
    
    \item The \textbf{API Routing} component invokes the \textbf{find()} function of the \textbf{Database Handler} to retrieve the user's trip data.
    
    \item The \textbf{Database Handler} queries the database and returns the user's trips to the \textbf{API Routing} component.
    
    \item The \textbf{API Routing} component performs an additional query for \textbf{DayDetails} data to calculate cost distributions and activity statistics.
    
    \item The \textbf{Database Handler} returns the requested \textbf{DayDetails} data to the \textbf{API Routing} component.
    
    \item The \textbf{API Routing} component aggregates the retrieved data and calculates dashboard statistics. If the user has no travel history, fallback demo data is generated.
    
    \item The \textbf{API Routing} component returns the aggregated statistics payload to the \textbf{dashboardService}.
    
    \item The \textbf{dashboardService} forwards the processed data to the \textbf{DashboardPage}.
    
    \item The \textbf{DashboardPage} renders the charts, summary statistics, and recent trip information for the user.
\end{enumerate}

\subsection{Detailed Analysis of User manages locations and activities Module}

The system administrator accesses the system through the \textbf{LocationManagementPage} component, which provides functionality for viewing and managing geospatial location data.

When the page is accessed, the system performs the following operations:

\begin{enumerate}
    \item The system automatically retrieves the list of available locations by invoking the \textbf{list\_locations()} function, which belongs to the \textbf{Location API} handler.
    
    \item The administrator may search for specific locations using keywords. In this case, the system performs a filtered query by invoking the \textbf{list\_locations()} function with the appropriate query parameters.
    
    \item To add a new location, the administrator selects the \textbf{Add Location} option, which navigates to the \textbf{AddLocationPage}.
    
    \item After entering the required information, such as location name, address, and category, and clicking the \textbf{Save} button, the system creates a new location by invoking the \textbf{add\_location()} function, which belongs to the \textbf{Location API} handler.
    
    \item When the administrator selects an existing location from the list, the system displays the \textbf{LocationDetailPage}, which provides detailed information about the selected location.
    
    \item The administrator may modify the location information through the \textbf{LocationDetailPage}. The system processes the update by invoking the \textbf{edit\_location()} function, which belongs to the \textbf{Location API} handler.
    
    \item The administrator may also remove a location from the system. This operation is performed by invoking the \textbf{delete\_location()} function, which belongs to the \textbf{Location API} handler.
    
    \item All location management operations, including viewing, creating, updating, and deleting locations, require administrator-level authorization.
\end{enumerate}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/analysis_phase_erd_mng_locations.png}
    \caption{Functional Analysis Class Diagram}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[scale=0.4]{Diagrams/analysis_phase_seq_mng_locations.png}
    \caption{Functional Analysis Sequence Diagram}
\end{figure}

\subsubsection{Functional Analysis Sequence Diagram}

The sequence of interactions for the Location Management Module is described as follows:

\begin{enumerate}
    \item The administrator accesses the \textbf{LocationManagementPage}.
    
    \item The \textbf{LocationManagementPage} invokes the \textbf{Location API} to retrieve the list of locations.
    
    \item The \textbf{Location API} requests location data from the \textbf{Database Handler}.
    
    \item The \textbf{Database Handler} queries the database and returns the list of locations to the \textbf{Location API}.
    
    \item The \textbf{Location API} returns the location list to the \textbf{LocationManagementPage}.
    
    \item The \textbf{LocationManagementPage} displays the retrieved locations to the administrator.
    
    \item The administrator selects the \textbf{Add Location} option.
    
    \item The system navigates the administrator from the \textbf{LocationManagementPage} to the \textbf{AddLocationPage}.
    
    \item The administrator enters the location information and clicks the \textbf{Save} button.
    
    \item The \textbf{AddLocationPage} invokes the \textbf{add\_location()} function of the \textbf{Location API}.
    
    \item The \textbf{Location API} inserts the new location into the database through the \textbf{Database Handler}.
    
    \item The \textbf{Database Handler} confirms the successful insertion.
    
    \item The \textbf{Location API} returns a success response to the \textbf{AddLocationPage}.
    
    \item The \textbf{AddLocationPage} displays a success notification to the administrator.
    
    \item The administrator selects a location from the list to view its details.
    
    \item The system navigates to the \textbf{LocationDetailPage}.
    
    \item The administrator modifies the location information and clicks the \textbf{Save} button.
    
    \item The \textbf{LocationDetailPage} invokes the \textbf{edit\_location()} function of the \textbf{Location API}.
    
    \item The \textbf{Location API} updates the location information in the database through the \textbf{Database Handler}.
    
    \item The \textbf{Database Handler} confirms the successful update.
    
    \item The \textbf{Location API} returns a success response to the \textbf{LocationDetailPage}.
    
    \item The \textbf{LocationDetailPage} displays a successful update notification.
    
    \item The administrator chooses to delete the location.
    
    \item The \textbf{LocationDetailPage} invokes the \textbf{delete\_location()} function of the \textbf{Location API}.
    
    \item The \textbf{Location API} deletes the location from the database through the \textbf{Database Handler}.
    
    \item The \textbf{Database Handler} confirms the successful deletion.
    
    \item The \textbf{Location API} returns a success response and redirects the administrator back to the \textbf{LocationManagementPage}.
    
    \item The \textbf{LocationManagementPage} displays a successful deletion notification and refreshes the location list.
\end{enumerate}

\chapter{Design}

\section{Data Storage Architecture}

The Traplanner system adopts a \textbf{Polyglot Persistence} architecture. Therefore, entities are divided into two primary storage groups:

\subsection{MongoDB Entities (Unstructured and Transactional Data)}

\begin{itemize}
\item \textbf{Users:} Stores user information such as \texttt{userId}, \texttt{username}, \texttt{email}, and \texttt{password}.

\item \textbf{Trips:} Contains general information about a trip, including: \texttt{tripId}, \texttt{userId}, \texttt{destination}, \texttt{totalBudget}, \texttt{status}, and \texttt{createdAt}.

\item \textbf{DayDetails:} Represents the detailed itinerary for each day within a trip. Includes \texttt{tripId}, \texttt{dayNumber}, \texttt{dayScheduleDetailedId}, and \texttt{dayActs}. The \texttt{dayActs} field is an array of activities (\texttt{startTime}, \texttt{endTime}, \texttt{location}, \texttt{price}).

\item \textbf{Locations:} Stores detailed information about static locations such as accommodations (Hotel), eateries (Restaurant), attractions (Attraction), and transportations (Transport). Includes attributes like \texttt{locationId}, \texttt{name}, \texttt{category}, \texttt{address}, \texttt{estimatedPrice}/\texttt{price\_range}, and \texttt{img\_url}.

\item \textbf{Reviews:} Stores user ratings and feedback for specific locations. Includes \texttt{locationId}, \texttt{userName}, \texttt{rating}, \texttt{comment}, and \texttt{createdAt}.

\end{itemize}

\subsection{Neo4j Entities (Spatial Graph Data)}

\begin{itemize}
\item \textbf{Province:} Nodes representing major provinces or cities.

\item \textbf{Ward:} Nodes representing smaller administrative areas (wards/communes) within a province.

\item \textbf{Location:} Nodes representing specific places (such as accommodations, eateries, and attractions) linked to their respective administrative wards.

\item \textbf{Transportation:} Nodes representing transport routes or options available between different cities or provinces.

\end{itemize}

\section{Relationship Definition}

The relationships between entities are represented through MongoDB references and Neo4j graph edges:

\subsection{Relationships in MongoDB}

\begin{itemize}
\item \textbf{User -- Trip (1:N):} A user can have multiple trips, linked via the \texttt{userId} field in the Trip document.

\item \textbf{Trip -- DayDetail (1:N):} A trip consists of multiple day details, linked via the \texttt{tripId} field.

\item \textbf{Location -- Review (1:N):} A location can have multiple reviews, linked via the \texttt{locationId} field in the Review document.

\end{itemize}
\textit{(Note: Chat memory and threads are not stored in MongoDB but managed transiently via Redis Cache for rapid retrieval).}

\subsection{Relationships in Neo4j Graph Space}

\begin{itemize}
\item \textbf{HAS (Province $\rightarrow$ Ward):} Represents a containment relationship, where a Province contains multiple Wards.

\item \textbf{LOCATED\_IN (Location $\rightarrow$ Ward):} Represents the geospatial relationship linking a specific location to its administrative Ward.

\end{itemize}




\section{Generate Trip}
% Overview of the automatic trip planning feature.

\subsection{Architecture Design}
The Trip Planner feature is powered by a \textbf{Multi-Agent Pipeline} implemented using LangGraph.

\begin{itemize}
\item Detailed description of workflow nodes:
\begin{itemize}
    \item \textbf{Extractor Node}: Responsible for receiving user input and applying an LLM to extract information into a standardized JSON structure. The output includes: \texttt{TripMetadata} (basic information), \texttt{TravelPreferences} (travel preferences), and \texttt{Constraints} (budget and health constraints). Notably, this node is capable of implicit inference, automatically deducing hidden preferences based on the participants of the trip.
    
    \item \textbf{Planner Node}: Handles the selection of locations from real-world databases (Neo4j and MongoDB). This process follows a two-step pipeline: Hard Filtering (eliminating options that violate constraints such as budget, time, and health) and Priority Scoring (ranking based on pace and travel style) to produce the most feasible list of hotels, activities, and restaurants.
    
    \item \textbf{Mobility Node}: Manages transportation logic using a two-layer architecture (Logic-First, AI-Refined). The first layer applies search algorithms to compute distance, cost, and filter options based on budget. The second layer re-ranks transportation options to better align with the user’s preferred style and desired experience.
    
    \item \textbf{Scheduler Node}: Takes the list of feasible locations and uses an LLM to generate a detailed day-by-day itinerary. This node ensures temporal consistency (morning to evening flow), while also calculating travel time, rest periods, and estimating cost distribution.
    
    \item \textbf{Validation Node}: Acts as a Quality Assurance Gate. It evaluates the itinerary comprehensively based on criteria such as budget, time, health, service quality, and route feasibility. The output includes scores, warnings, and triggers a feedback loop to request itinerary adjustments if critical issues are detected.
    
    \item \textbf{Generate Answer Node}: Aggregates all structured trip data and uses a large language model (Gemini) to generate a natural language response in Vietnamese. The output is formatted with a clear structure including: summary, detailed itinerary, cost analysis, logistics information, and recommendations. Additionally, this node produces a schema for database storage.
\end{itemize}
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.8]{Diagrams/workflow_mermaid.png}
\end{figure}

\item The system interacts with a \textbf{Polyglot Database}:
\begin{itemize}
    \item Spatial queries are handled by Neo4j.
    \item Static and transactional data are retrieved from MongoDB.
\end{itemize}

\end{itemize}


% (Suggestion: Insert UML Sequence Diagram here.)

\section{User using Chatbot}


\subsection{Architecture Design}
\begin{itemize}
\item Detailed description of node functions in the chatbot architecture:
\begin{itemize}
    \item \textbf{Memory Init Node (Memory Initialization)}: This node is responsible for establishing the initial state of the agent by managing hierarchical memory. Specifically, the system retrieves short-term memory (recent conversation turns) from Redis Cache to maintain conversational continuity. At the same time, long-term memory (summarized interaction history) is also loaded to enable the agent to capture user preferences and deeper contextual understanding from previous sessions.
    
    \item \textbf{Classify Query Node (Query Classification)}: Acts as a Smart Router. This node leverages a Large Language Model (LLM) to analyze the user's intent (Intent Classification). Queries are categorized into groups such as casual conversation (chit-chat) or complex task-oriented requests requiring itinerary-related data retrieval. This classification optimizes workflow routing and reduces computational overhead.
    
    \item \textbf{Retrieve Trip Context Node (Trip Context Retrieval)}: When a query is identified as task-related, this node is activated to fetch the complete trip data from the database (including destinations, total budget, and detailed day-by-day itinerary). The retrieved data is formatted into a structured context and injected into the system prompt. This process significantly reduces hallucination by forcing the LLM to reason based on factual data.
    
    \item \textbf{Agent Node (Core Processing Agent)}: This is the central component of the system, designed following the ReAct (Reasoning and Acting) architecture. The agent receives all inputs, including trip context, conversation history, and the current query. The LLM then performs reasoning to decide whether to generate a direct response or invoke tool calls to interact with external data (e.g., searching for alternative hotels, updating itinerary activities). This loop continues until the user’s request is fully resolved.
    
    \item \textbf{Tool Node (Tool Execution)}: Responsible for handling tool calls issued by the Agent Node. This node wraps a set of Python functions that execute real-world operations such as \texttt{search\_alternative\_hotels}, \texttt{update\_trip\_activity}, and \texttt{calculate\_trip\_budget}. After executing database queries or logical computations, the results are formatted and returned to the Agent Node for further reasoning.
    
    \item \textbf{Direct Response Node (Direct Response)}: A lightweight processing path dedicated to simple conversational queries such as greetings or general questions that do not require database interaction. By routing such queries to this node, the system minimizes latency and avoids unnecessary activation of the ReAct agent loop, resulting in a smoother user experience.
    
    \item \textbf{Memory Save Node (State Persistence)}: The final step in the LangGraph execution flow. This node synchronizes the latest conversation state back to Redis storage. Additionally, it includes an automatic context-length monitoring mechanism: when the number of messages exceeds a predefined threshold, a secondary LLM process is triggered to summarize older conversations. These summaries are then stored to update long-term memory, preventing context window overflow in future interactions.
\end{itemize}
\begin{figure}[H]
    \centering
    \includegraphics[scale=0.8]{Diagrams/chatbot_mermaid.png}
\end{figure}
\end{itemize}

\section{Viewing Trips Statistics}

The Trips Statistics feature provides users with an overview of their travel history through key performance indicators (KPIs) and interactive visualizations, computed dynamically by the backend.

\subsection{User Interface Design}
Based on structured data from the API, the frontend visualizes the information into the following components:
\begin{itemize}
    \item \textbf{KPI Cards}:
    \begin{itemize}
        \item Provide a quick overview of total trips, upcoming trips, and unique destinations visited.
        \item Display the cumulative total budget, aggregated from all trips in the user's history.
    \end{itemize}
    \item \textbf{Charts}:
    \begin{itemize}
        \item \textbf{Pie Charts}: Represent cost distribution, allowing users to visually understand the proportion of the budget spent across different expense categories (Stay, Food, Activity, Transport, Other).
        \item \textbf{Bar Charts}: Display the number of trips generated per month (based on the \texttt{createdAt} field), reflecting the user's travel planning trends over time.
    \end{itemize}
\end{itemize}

\subsection{Data Aggregation Design}
To ensure real-time responsiveness and avoid overloading the database with complex aggregation pipelines, the system employs an Application-Level Aggregation strategy within the Django backend. This approach efficiently combines lightweight MongoDB queries with optimized Python-based computational logic:

\begin{itemize}
    \item \textbf{Cross-Collection Resolution}: Instead of relying on heavy MongoDB \texttt{\$lookup} pipelines, the system first retrieves all active \texttt{tripId}s from the \texttt{Trips} collection and performs a secondary batch query on the \texttt{DayDetails} collection using the \texttt{\$in} operator. This decoupled querying strategy significantly reduces database lock contention.
    \item \textbf{Temporal Aggregation}: To construct the trips-per-month data, the \texttt{createdAt} timestamps are parsed and bucketed by month (e.g., \texttt{YYYY-MM}) utilizing Python's \texttt{collections.defaultdict}. This structure enables a highly efficient $O(N)$ single-pass iteration over the trip records.
    \item \textbf{Cost Distribution Mapping}: The system dynamically iterates through nested activity arrays (\texttt{dayActs}) within the retrieved \texttt{DayDetails} documents. It accumulates the \texttt{price} attributes and groups them by activity \texttt{type}. The aggregated data is then transformed into a structured array to seamlessly power the frontend charts.
    \item \textbf{Fallback Mechanism}: If a newly registered user lacks historical data, the backend logic automatically retrieves a set of high-quality ``demo trips'' to populate the dashboard, ensuring a welcoming and engaging onboarding experience rather than an empty screen.
\end{itemize}

\section{Locations and Activities Management}

The Locations and Activities Management module empowers system administrators to maintain the foundation of real-world geospatial data used by the AI Planner. This module ensures strict synchronization between unstructured descriptions and spatial routing graphs.

\subsection{Polyglot Synchronization Architecture}
Whenever an administrator adds, updates, or deletes a location, the backend simultaneously applies modifications to both databases to guarantee data consistency:
\begin{itemize}
    \item \textbf{MongoDB (Detailed Attributes)}: The \texttt{Locations} collection stores rich textual and media data, including \texttt{name}, \texttt{category} (Stay, Food, Activity, Transport), \texttt{address}, \texttt{price\_range}, and \texttt{img\_url}. This data is fetched by the AI to generate descriptive itineraries.
    \item \textbf{Neo4j (Spatial Topology)}: Simultaneously, a Cypher query is executed to create or merge a \texttt{Location} node and structurally link it to a specific \texttt{Ward} node via a \texttt{LOCATED\_IN} relationship. For transport routes, a distinct \texttt{Transportation} node is created containing departure/arrival properties and durations.
\end{itemize}

\subsection{Review and Rating Aggregation}
To maintain the quality of suggested destinations, the system supports a user feedback mechanism:
\begin{itemize}
    \item When a user submits a review for a specific location, the feedback is stored as a new document in the \texttt{Reviews} collection.
    \item The backend triggers an aggregation pipeline (\texttt{\$group} and \texttt{\$avg}) to recalculate the mean rating of that \texttt{locationId}.
    \item The resulting average rating is then directly updated back into the \texttt{rating} field of the parent document in the \texttt{Locations} collection. This denormalized approach allows the AI Planner to quickly filter and recommend top-rated places without computing averages on the fly.
\end{itemize}
\chapter{Implementations}
\section{Source Code and Structure of Project}
\section{Trip Planner}
\subsection{Interfaces}
\subsection{Evaluation}
\subsection{Improvements}
\section{Chat about Trip}
\subsection{Interfaces}
\subsection{Evaluation}
\subsection{Improvements}
\section{Trips Statistics Dashboard}
\section{Locations and Actvities Management}
\chapter{Citations}
[1] https://www.ibm.com/think/topics/large-language-models
[2] https://www.ibm.com/think/topics/multiagent-system
[3] https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
[4] https://arxiv.org/pdf/2509.08014
[5] https://arxiv.org/pdf/2501.09136
[6] https://arxiv.org/pdf/2210.03629
[7] https://arxiv.org/pdf/2506.07398
\cleardoublepage       % Ngắt trang sau khi mục lục kết thúc


\end{document}