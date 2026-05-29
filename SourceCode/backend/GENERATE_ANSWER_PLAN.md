# Generate_answer.py Implementation Plan

## 🎯 Overview

The **Generate_answer Node** is the final step in the travel planning pipeline that converts structured data (scheduling, activities, accommodations, transportations, validation results) into natural language responses using an LLM.

**Purpose**:
- Transform technical itinerary data into human-readable format
- Generate personalized trip recommendations
- Include cost summaries and logistics details
- Provide helpful tips and safety information
- Format output for both text and potential UI display

## 📊 Input Data

```
State {
  trip_metadata: {
    start_date: str,
    end_date: str,
    total_days: int,
    destination: str,
    age_range: tuple,
    ...
  }
  
  scheduling: [DaySchedule],  # Day-by-day itineraries
  activities: [Activity],      # Available activities
  accommodations: [Accommodation],  # Booked accommodations
  transportations: [Transportation],  # Transport routes
  constraints: {...},
  travel_preferences: {...},
  
  validation: {
    overall_score: float,
    status: str,
    category_scores: {...},
    issues: [...],
    recommendations: [...]
  }
}
```

## 📝 Output Format

```
{
  "summary": "Natural language overview of the trip",
  "detailed_itinerary": "Day-by-day breakdown with times and activities",
  "cost_breakdown": "Budget summary with cost categories",
  "logistics": "Transportation, accommodations, important info",
  "recommendations": "Tips and suggestions from validation",
  "safety_info": "Health, safety, and important local info",
  "full_response": "Complete formatted response for user"
}
```

## 🔧 Architecture

### Component 1: Data Formatter
Extracts and structures data from state for LLM context

```python
class TripDataFormatter:
  - format_schedule(scheduling) → structured text
  - format_costs(scheduling) → cost breakdown
  - format_logistics(accommodations, transportations) → logistics info
  - format_validation(validation) → validation summary
  - format_constraints(constraints, preferences) → trip context
```

### Component 2: Prompt Engineer
Creates contextualized prompts for different response types

```python
class PromptEngine:
  - create_summary_prompt(trip_data) → LLM prompt
  - create_detailed_prompt(trip_data) → LLM prompt
  - create_recommendations_prompt(validation_data) → LLM prompt
  - create_logistics_prompt(scheduling, accommodations) → LLM prompt
```

### Component 3: LLM Integration
Calls Google Generative AI to generate natural language

```python
class LLMGenerator:
  - initialize_client(api_key) → GoogleGenerativeAI
  - generate_summary(prompt, model='gemini-1.5-flash') → response
  - generate_detailed_response(prompt, model) → response
  - generate_multiple_sections(prompts) → {section: response}
```

### Component 4: Response Formatter
Formats LLM output into structured response

```python
class ResponseFormatter:
  - format_response(raw_responses) → formatted JSON
  - add_metadata(response, state) → response with metadata
  - create_user_friendly_output(response) → beautified text
```

## 📋 Implementation Steps

### Phase 1: Data Extraction & Formatting
1. Extract trip dates, destination, traveler info
2. Format daily schedule (times, activities, costs)
3. Calculate and format cost breakdowns
4. Format accommodation and transportation details
5. Extract validation results and recommendations

### Phase 2: Prompt Construction
1. Create summary prompt (1-2 paragraphs overview)
2. Create detailed itinerary prompt (day-by-day with times)
3. Create cost breakdown prompt (visual-friendly format)
4. Create logistics prompt (accommodation, transport, local info)
5. Create recommendations prompt (from validation + general tips)

### Phase 3: LLM Integration
1. Initialize Google Generative AI client
2. Call LLM with different prompts
3. Handle streaming vs complete responses
4. Add error handling and fallbacks
5. Cache responses if possible

### Phase 4: Response Assembly
1. Combine all LLM responses
2. Add structured metadata
3. Format for display (markdown, HTML, JSON)
4. Validate response quality
5. Return complete response

## 🎨 Prompt Templates (Tiếng Việt)

### Summary Prompt
```
Bạn là một trợ lý du lịch thân thiện. Hãy tạo một bản tóm tắt hấp dẫn gồm 2-3 câu về chuyến đi {{ days }} ngày đến {{ destination }}.

Chi tiết chuyến đi:
- Thời gian: {{ start_date }} đến {{ end_date }}
- Số du khách: {{ group_size }} người (tuổi: {{ age_range }})
- Phong cách: {{ travel_style }}
- Tốc độ: {{ travel_pace }}
- Ngân sách: {{ budget }} VNĐ

Lịch trình mẫu:
{{ sample_days }}

Hãy viết một bản tóm tắt hấp dẫn, nắm bắt được bản chất của chuyến đi này và điều gì làm nó đặc biệt.
```

### Detailed Itinerary Prompt
```
Hãy tạo một lịch trình chi tiết, dễ theo dõi cho chuyến đi {{ days }} ngày này.

Định dạng mỗi ngày như sau:
**Ngày {{ day }}: {{ theme }}**
- Sáng (06:00-12:00): [hoạt động với thời gian]
- Chiều (12:00-18:00): [hoạt động với thời gian]
- Tối (18:00-22:00): [hoạt động với thời gian]
- Chỗ ở: [tên khách sạn và thông tin]

Lịch trình chuyến đi:
{{ full_schedule }}

Bao gồm những mẹo thực tế như "đi giày thoải mái", "mang kem chống nắng", v.v. cho từng ngày.
Viết theo cách hấp dẫn và dễ hiểu.
```

### Cost Breakdown Prompt
```
Hãy tóm tắt chi phí cho chuyến đi này theo cách rõ ràng, dễ hiểu.

Chi tiết chi phí:
{{ cost_breakdown }}

Tổng ngân sách: {{ total_budget }} VNĐ
Tổng chi tiêu: {{ total_cost }} VNĐ
Còn lại: {{ remaining }} VNĐ

Hãy viết giải thích thân thiện về:
1. Chi phí nào cao nhất và tại sao
2. Cơ hội tiết kiệm nếu vượt ngân sách
3. Đánh giá mức sử dụng ngân sách
Bao gồm số liệu cụ thể và các danh mục.
```

### Logistics Prompt
```
Hãy cung cấp thông tin hậu cần thực tế cho các du khách trên chuyến đi này.

Chỗ ở:
{{ accommodations }}

Phương tiện giao thông:
{{ transportations }}

Tạo thông tin hữu ích bao gồm:
1. Thủ tục nhận phòng/trả phòng
2. Cách di chuyển giữa các địa điểm
3. Cách đến/rời sân bay
4. Thời gian di chuyển được đề xuất
5. Các tùy chọn giao thông địa phương
6. Các số điện thoại khẩn cấp
Viết theo cách thực tế và khả thi.
```

### Recommendations Prompt
```
Dựa trên kết quả xác thực chuyến đi, hãy cung cấp những gợi ý hữu ích.

Kết quả xác thực:
- Điểm số tổng thể: {{ overall_score }}
- Trạng thái: {{ status }}
- Vấn đề: {{ issues }}
- Gợi ý: {{ recommendations }}

Tạo những đề xuất được cá nhân hóa cho:
1. Cách cải thiện trải nghiệm
2. Những thứ cần mang hoặc chuẩn bị
3. Phong tục và văn hóa địa phương
4. Cân nhắc về an toàn
5. Mẹo sức khỏe và wellness

Hãy thân thiện, thực tế và cụ thể cho {{ destination }}.
```

## 🔄 Response Sections (Tiếng Việt)

### 1. Summary (2-3 câu)
Tóm tắt nhanh chuyến đi theo cách hấp dẫn

Ví dụ:
```
Chuyến phiêu lưu 3 ngày tại Quảng Ninh của bạn kết hợp vẻ đẹp tự nhiên tuyệt đẹp của Vịnh Hạ Long 
với sự phong phú văn hóa của các chợ địa phương. Bạn sẽ đi du thuyền qua những vách đá vôi, khám phá 
những hang động ẩn giấu và trải nghiệm sự hiếu khách Việt Nam chân thực – tất cả trong một ngân sách được 
lập kế hoạch cẩn thận 1,2 triệu VNĐ.
```

### 2. Ngày - Lịch trình chi tiết
Lịch trình chi tiết với thời gian, hoạt động và mẹo thực tế

Ví dụ:
```
**Ngày 1: Tới và Quen Thuận**
⏰ Thời gian: 4 giờ hoạt động

🚌 06:00 - Khởi hành từ Hà Nội
   Phương tiện: Xe buýt từ Hà Nội đến Hạ Long (120 phút)
   Chi phí: 68.000 VNĐ
   Mẹo: Mang nước và đồ ăn nhẹ cho hành trình

🏨 12:00 - Tới nơi & Nhận phòng khách sạn
   Chỗ ở: Khách sạn Hạ Long (3 sao thoải mái)
   Chi phí: 100.000 VNĐ/đêm
   Thông tin: Nằm ở trung tâm thành phố, cách bến tàu đi bộ

🍜 13:00 - Ăn trưa
   Chi phí: 100.000 VNĐ
   Gợi ý: Thử đặc sản "Cơm Cua" (cơm cua) địa phương

🏖️ 15:00 - Nghỉ ngơi & Khám phá khu vực
   Hoạt động miễn phí
   Mẹo: Kem chống nắng và mũ rất cần thiết

🍲 19:00 - Ăn tối
   Chi phí: 120.000 VNĐ
   Mẹo: Đặt phòng khách sạn để được gợi ý địa phương
```

### 3. Tóm tắt Chi phí
Phân tích chi phí và mức sử dụng ngân sách

Ví dụ:
```
**💰 Phân Tích Chi Phí Chuyến Đi**

💰 Tổng ngân sách: 1.500.000 VNĐ
💰 Tổng chi tiêu: 1.196.000 VNĐ
✅ Còn lại: 304.000 VNĐ (20% dự phòng)

Chi phí theo danh mục:
🚌 Phương tiện giao thông: 284.000 VNĐ (24%)
  - Bus Hà Nội → Hạ Long x2: 136.000 VNĐ

🏨 Chỗ ở: 200.000 VNĐ (17%)
  - Khách sạn Hạ Long x2 đêm: 200.000 VNĐ

🎫 Hoạt động: 280.000 VNĐ (23%)
  - Du thuyền Vịnh Hạ Long: 150.000 VNĐ
  - Hang động Sơn Sung: 80.000 VNĐ
  - Bãi Titop Island: 50.000 VNĐ

🍽️ Ăn uống: 432.000 VNĐ (36%)
  - Ăn sáng x3: 240.000 VNĐ
  - Ăn trưa x3: 300.000 VNĐ
  - Ăn tối x3: 360.000 VNĐ

Tình trạng ngân sách: ✅ XUẤT SẮC - 80% sử dụng, dự phòng tốt
```

### 4. Thông tin Hậu Cần & Thực Tế
Chỗ ở, phương tiện và thông tin hữu ích

Ví dụ:
```
**🏨 Chỗ Ở**
- Đêm 1-2: Khách sạn Hạ Long
  Địa chỉ: 123 Đường chính, Hạ Long
  Nhận phòng: 14:00, Trả phòng: 11:00
  Liên hệ: +84-33-123-4567
  Dịch vụ: WiFi, Điều hòa, Nhà hàng

**🚌 Di Chuyển**
- Hà Nội → Hạ Long: Bus, 120 phút, 68.000 VNĐ
- Hạ Long → Hà Nội: Bus, 120 phút, 68.000 VNĐ
- Trong Hạ Long: Đi bộ (trung tâm thành phố), taxi cho khoảng cách xa
- Du thuyền: Bao gồm trong giá vé

**💡 Mẹo Thực Tế**
- Tiền tệ: Đồng Việt Nam (VNĐ)
- Thời gian tốt nhất: Tháng 10-4
- Mặc: Quần áo nhẹ, thoải mái; mang áo khoác cho hang động
- Ngôn ngữ: Tiếng Anh được nói ở khu du lịch
- Khẩn cấp: 113 (cứu hỏa), 114 (cứu thương), 116 (cảnh sát)
```

### 5. Gợi Ý & Mẹo
Từ xác thực và mẹo du lịch chung

Ví dụ:
```
**✨ Mẹo Nâng Cao Trải Nghiệm**

1. **Đa Dạng Hoạt Động**
   Gợi ý: Bạn có 3 hoạt động tự nhiên. Hãy xem xét thêm 1 hoạt động văn hóa 
   (ví dụ: Chợ biên giới Mong Cái) để đa dạng hơn.

2. **Tốc Độ Du Lịch**
   Lịch trình của bạn cân bằng tốt với khoảng thời gian nghỉ ngơi tốt. Ngày 2 
   hoạt động nhất với 6 giờ hoạt động. Cân nhắc khởi hành sớm (6 sáng) để tránh đông đúc.

3. **Ngân Sách**
   Bạn đang sử dụng 80% ngân sách với 20% dự phòng. Điều này xuất sắc cho 
   chi phí bất ngờ hoặc nâng cấp.

4. **Sức Khỏe & An Toàn**
   - Mang kem chống nắng (tia UV mạnh ở vùng này)
   - Uống nước đầy đủ (mang bình nước)
   - Giày đi bộ thoải mái là cần thiết
   - Bảo hiểm du lịch được khuyến nghị

5. **Trải Nghiệm Địa Phương**
   - Thử hải sản tươi tại chợ đêm Hạ Long
   - Trò chuyện với ngư dân địa phương vào buổi sáng
   - Ghé chợ sáng (6-7 sáng) để có trải nghiệm chân thực
   - Học một vài cụm từ tiếng Việt – người dân sẽ đánh giá cao nỗ lực

6. **Mẹo Tiết Kiệm Ngân Sách**
   - Ăn ở nhà hàng địa phương thay vì du lịch (tiết kiệm 30-40%)
   - Dùng phương tiện công cộng khi có
   - Mặc cả ở chợ (chiết khấu điển hình: 10-20%)
   - Đặt hoạt động trực tiếp với các nhà khai thác để bỏ qua trung gian
```

## 🎯 Implementation Details

### Initialize LLM Client
```python
from google.generativeai import GenerativeAI

def initialize_llm(api_key: str):
    """Initialize Google Generative AI client"""
    client = GenerativeAI(api_key=api_key)
    return client
```

### Generate Single Section
```python
def generate_section(client, prompt: str, section_name: str, model: str = "gemini-1.5-flash"):
    """Generate a single response section using LLM"""
    try:
        response = client.generate_content(prompt)
        return {
            "section": section_name,
            "content": response.text,
            "tokens_used": response.usage_metadata.total_tokens if hasattr(response, 'usage_metadata') else None
        }
    except Exception as e:
        logger.error(f"Error generating {section_name}: {e}")
        return {
            "section": section_name,
            "content": f"Unable to generate {section_name}. {str(e)}",
            "error": True
        }
```

### Generate Multiple Sections in Parallel
```python
def generate_response_sections(client, prompts: Dict[str, str], model: str = "gemini-1.5-flash"):
    """Generate multiple sections concurrently"""
    responses = {}
    for section_name, prompt in prompts.items():
        responses[section_name] = generate_section(client, prompt, section_name, model)
    return responses
```

### Format Final Response
```python
def format_final_response(responses: Dict, state: Dict) -> Dict:
    """Assemble all sections into final response"""
    return {
        "summary": responses.get("summary", {}).get("content", ""),
        "detailed_itinerary": responses.get("itinerary", {}).get("content", ""),
        "cost_breakdown": responses.get("costs", {}).get("content", ""),
        "logistics": responses.get("logistics", {}).get("content", ""),
        "recommendations": responses.get("recommendations", {}).get("content", ""),
        
        "metadata": {
            "trip_dates": f"{state['trip_metadata']['start_date']} - {state['trip_metadata']['end_date']}",
            "destination": state['trip_metadata']['destination'],
            "total_days": state['trip_metadata']['total_days'],
            "traveler_count": state['constraints']['group_size'],
            "total_budget": state['constraints']['travel_budget'],
        },
        
        "validation_status": {
            "overall_score": state.get('validation', {}).get('overall_score'),
            "status": state.get('validation', {}).get('status'),
            "approved": state.get('validation', {}).get('is_valid')
        },
        
        "full_response": "\n\n".join([
            responses.get("summary", {}).get("content", ""),
            responses.get("itinerary", {}).get("content", ""),
            responses.get("costs", {}).get("content", ""),
            responses.get("logistics", {}).get("content", ""),
            responses.get("recommendations", {}).get("content", "")
        ])
    }
```

## 🚀 Node Entry Point

```python
def generate_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main generate_answer node for workflow
    
    Input:
    - scheduling: List[Dict] - Complete day-by-day itinerary
    - activities, accommodations, transportations: Lists of booked items
    - validation: ValidationResult with scores and recommendations
    - constraints, travel_preferences: User input
    - trip_metadata: Basic trip info
    
    Output:
    - generated_response: Dict with all formatted sections
    - full_response: Complete formatted response for user
    """
    
    # Initialize LLM
    api_key = os.getenv("GOOGLE_API_KEY")
    client = initialize_llm(api_key)
    
    # Format data for LLM
    formatter = TripDataFormatter(state)
    
    # Create prompts
    prompt_engine = PromptEngine(formatter)
    prompts = {
        "summary": prompt_engine.create_summary_prompt(),
        "itinerary": prompt_engine.create_detailed_prompt(),
        "costs": prompt_engine.create_costs_prompt(),
        "logistics": prompt_engine.create_logistics_prompt(),
        "recommendations": prompt_engine.create_recommendations_prompt()
    }
    
    # Generate response sections
    responses = generate_response_sections(client, prompts)
    
    # Format final response
    final_response = format_final_response(responses, state)
    
    # Add to state
    state["generated_response"] = final_response
    state["response"] = final_response["full_response"]
    
    return state
```

## ✅ Success Criteria

- ✅ Extracts all relevant data from state without errors
- ✅ Creates well-structured, contextual prompts
- ✅ Generates natural, engaging language using LLM
- ✅ Formats responses into clear sections
- ✅ Handles LLM errors gracefully with fallbacks
- ✅ Includes metadata and validation status
- ✅ Response is suitable for user display
- ✅ Comprehensive coverage of trip details
- ✅ Personalized based on user preferences
- ✅ Practical tips and safety information included

## 🔧 Configuration

```python
# LLM Configuration
LLM_CONFIG = {
    "model": "gemini-1.5-flash",  # Fast, cost-effective
    "temperature": 0.7,  # Balanced creativity
    "max_tokens": 1000,  # Reasonable length per section
    "top_p": 0.9,  # Diverse but focused
}

# Fallback responses if LLM fails
FALLBACK_RESPONSES = {
    "summary": "Trip summary unavailable. Please check trip details.",
    "itinerary": "Detailed itinerary unavailable. Check scheduling data.",
    "costs": "Cost breakdown unavailable.",
    "logistics": "Logistics information unavailable.",
    "recommendations": "Recommendations unavailable."
}
```

## 📊 Response Quality Checks

1. **Content Validation**: Ensure LLM response is not empty/null
2. **Length Check**: Verify response length is reasonable (not too short)
3. **Format Check**: Ensure sections are properly structured
4. **Data Accuracy**: Validate numbers and dates match source data
5. **Grammar Check**: Optionally run spell check on response
6. **Hallucination Check**: Ensure response doesn't mention false information

## 🔗 Integration Points

**Upstream** (Input from):
- Extractor → Trip metadata, preferences, constraints
- Planner → Activities, accommodations, transportations
- Scheduler → Complete day-by-day scheduling
- Validation → Scores, issues, recommendations

**Downstream** (Output to):
- API Response → Send to frontend/user
- Email → Send formatted email
- PDF Export → Generate PDF itinerary
- Chat → Integration with chatbot

## 📈 Future Enhancements

1. **Multi-language Support**: Generate responses in Vietnamese, English, etc.
2. **Custom Formatting**: Support different output formats (email, PDF, web)
3. **Response Caching**: Cache LLM responses for common destinations
4. **Personalization**: Adjust tone based on user profile
5. **Alternative Suggestions**: Generate 2-3 alternative itineraries
6. **Weather Integration**: Include weather forecast in recommendation
7. **Real-time Pricing**: Update costs with current exchange rates
