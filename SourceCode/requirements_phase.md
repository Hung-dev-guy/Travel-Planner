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