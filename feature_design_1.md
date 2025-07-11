

# **大模型中文语音转文字及逐字时间戳方案深度分析报告**

## **I. 引言**

### **背景与需求概述：中文语音转文字与逐字时间戳的重要性**

自动语音识别（ASR）技术已成为现代人机交互、内容生产与分析领域不可或缺的核心技术。随着人工智能大模型在自然语言处理领域的突破，ASR的识别准确率、鲁棒性及功能丰富性得到了前所未有的提升，极大地拓宽了其应用边界。在当前数字化浪潮下，对中文语音转文字的需求日益增长，尤其是在会议记录自动化、视频内容字幕生成、智能客服系统、在线教育辅助工具以及媒体内容分析等多个垂直领域。

逐字时间戳（Word-level Timestamps）功能已从一个辅助特性演变为一项核心需求。它能够提供文本与原始音频之间精确到毫秒级的同步信息，这对于生成高质量、可编辑的视频字幕、实现音频内容的高效检索与导航、辅助音频/视频的后期编辑与分析，以及构建更具交互性的多媒体应用至关重要 1。例如，Google Cloud Speech-to-Text明确指出时间偏移值有助于分析长音频文件，方便用户在转录文本中搜索特定词语并在原始音频中定位 4。

将逐字时间戳视为高级应用的关键推动因素，其重要性体现在多个层面。最初的ASR输出通常是纯文本，而句级时间戳仅能提供基本的同步信息。然而，研究材料中反复强调“逐字时间戳” 1 表明了行业趋势和用户预期的显著提升。例如，逐字时间戳在确保音频与文本之间精确同步方面发挥着关键作用，这对于字幕制作、搜索索引或创建交互式文本至关重要 1。它还带来改进的搜索能力、音视频同步以及音频编辑的便利性 3。这些功能表明，逐字时间戳并非简单的功能增强，而是支持新一代交互式和高功能性音视频应用的基础。所报告的时间戳精度（例如，Canary模型中逐字时间戳的误差范围为20-120毫秒） 2 进一步突显了其技术成熟度和对高保真同步的需求。

### **报告目标与结构：评估主流大模型方案，提供性能、成本及应用建议**

本报告旨在深入分析当前市场上主流的中文ASR大模型方案，涵盖云服务提供商和开源解决方案。报告将重点评估这些方案在中文语音转文字的识别准确率、逐字时间戳的精度与可用性、以及多语种/方言支持等核心能力方面的表现。报告还将综合考量各方案的技术优势、潜在局限性、部署的灵活性（云端与私有化部署）、以及总体拥有成本（TCO）等实际考量因素，旨在为技术项目经理和工程师提供数据驱动的决策依据，以选择最符合其业务需求和预算的ASR解决方案。

## **II. 语音转文字 (ASR) 与逐字时间戳技术概述**

### **核心概念：自动语音识别 (ASR) 与逐字时间戳**

**ASR (Automatic Speech Recognition)**：ASR，又称语音转文本（Speech-to-Text, STT），是计算机系统将口语单词和短语从音频中解码并转录成书面文本的能力 9。一个典型的ASR系统通常包含声学模型（Acoustic Model）、语言模型（Language Model）和解码器（Decoder）等核心组件，它们协同工作以将语音信号转换为可读文本。

**逐字时间戳 (Word-level Timestamps)**：在ASR输出的文本中，逐字时间戳为每个识别出的词语（或汉字）提供其在原始音频中的精确起始和结束时间信息 1。这些时间信息通常以毫秒为单位（如阿里云） 6，或以100毫秒为增量（如Google Cloud） 4。这种精细的时间信息对于需要文本与音频高度同步的应用至关重要。

现代ASR模型中逐字时间戳的底层机制及其效率影响值得关注。研究材料反复提及“强制对齐”（force-alignment） 2 作为获取时间戳的方法。传统上，这通常是一个单独的后处理步骤，会增加额外的计算开销。然而，现代的端到端ASR系统，特别是像FunASR的Paraformer这样的非自回归模型，正在将时间戳预测直接整合到识别过程中，利用“连续积分与触发”（Continuous Integrate-and-Fire, CIF）等机制 11。FunASR明确指出，这种集成消除了对单独对齐机制的需求，并且“对于商业用途很有价值，因为它有助于减少计算和时间开销” 12。OpenAI Whisper也通过专门的

\<|timestamp|\>标记来预测时间戳 2，而

whisper-timestamped等工具则进一步优化了这些时间戳 5。这种技术发展标志着ASR架构向集成式、单通道时间戳预测的重大转变。这种集成至关重要，因为它直接影响推理延迟和计算成本，通过避免多阶段处理的开销，使得这些模型更适用于实时和高吞吐量的商业应用。

### **技术重要性与典型应用场景**

逐字时间戳技术在多个领域具有显著的应用价值：

* **提高内容可访问性**：为听力障碍者提供精确同步的实时字幕，或为视频内容生成高质量的SRT/VTT字幕文件，确保信息无障碍传播 1。  
* **高效内容检索与导航**：用户可以通过转录文本中的关键词，利用逐字时间戳快速定位到音频或视频中的精确位置，这对于处理会议记录、访谈、课堂笔记、法律诉讼记录等长篇内容尤为重要 1。  
* **辅助内容编辑与生产**：内容创作者可以基于时间戳进行精确的音频剪辑、视频配音字幕制作，或进行内容分析（如情绪分析、说话人识别） 3。  
* **智能交互与分析**：支持更复杂的智能客服、语音助手、语音命令系统，以及对语音内容进行更深层次的情感、意图分析 10。

### **准确率衡量标准：词错误率 (WER) 与字错误率 (CER)**

* **WER (Word Error Rate)**：是衡量ASR系统准确率的主要指标之一。它计算整个转录文本中不正确词语的百分比，WER越低表示系统越准确 9。WER的计算公式为 (S+I+D)/N，其中S为替换错误（Substitution），I为插入错误（Insertion），D为删除错误（Deletion），N为标准答案（Ground Truth）中的总词数 20。  
* **CER (Character Error Rate)**：对于中文等非空格分隔语言，CER是更常用的衡量指标，它衡量字符级别的错误率 13。  
* **标准答案 (Ground Truth)**：为了准确评估ASR系统的性能，需要一个100%准确的人工转录文本作为“标准答案”，与机器转录结果进行比较 9。

在实际应用中，ASR模型的准确率基准测试面临挑战，同时领域特定准确率的重要性也日益凸显。虽然WER/CER是标准的评估指标 9，但研究材料明确警告，使用开源语料库进行基准测试可能会产生不具代表性的结果，因为模型可能“记住”训练数据 20。此外，多份材料指出真实世界中文ASR面临的显著挑战，包括“不同方言和发音”、“口音和语音变化”、“定制或特定领域的词汇和缩略语”以及“词语的语境关系” 24。其中一份材料特别提到，当前行业缺乏中文ASR的系统性标准测试和测试集，导致模型在“真实对话数据”和“专业/生活类细分语料库”上的准确率表现不一 25。这表明，在公开学术基准测试（如AISHELL）上报告的WER/CER虽然有助于进行一般性比较，但它们可能无法完全反映模型在特定、嘈杂或专业术语繁多的真实用例中的性能。因此，要确定“最佳”解决方案，需要超越基准数字，考虑模型在目标应用独特音频特征下的鲁棒性、适应性和定制能力。

## **III. 主流大模型方案分析**

### **A. 云服务提供商方案**

云服务提供商的ASR方案通常以API或SDK的形式提供，具有易于接入、高可用性、弹性可扩展性强等优势。用户无需自建和维护复杂的底层基础设施，通常按量计费，适合快速上线和应对不确定性负载。

#### **1\. 阿里云智能语音交互 (Alibaba Cloud Intelligent Speech Interaction)**

* **核心能力与逐字时间戳支持**：  
  * 阿里云智能语音交互服务提供“一句话识别”（实时短语音识别）、“实时语音识别”（实时长语音识别）和“录音文件识别”（离线文件识别）等多种产品形态 28。  
  * 其“实时语音识别”服务支持无限长音频流的实时转录，并提供智能断句和句级时间戳 30。  
  * 明确支持“字级别音素边界接口”，即逐字时间戳功能，可输出每个汉字/英文单词在音频中的时间位置 6。用户需在客户端设置  
    enable\_subtitle 为 true 来开启此功能 6。  
  * API响应中包含一个 words 列表，其中每个词对象都包含 text, startTime, 和 endTime 等详细时间信息 7。  
* **中文识别准确率表现**：  
  * 阿里云声称其通用字准确率在90%以上，部分模型可达98% 30。  
  * 然而，文档中未直接提供中文逐字时间戳的精确准确率（如毫秒级误差）数据 30。  
  * 值得注意的是，ASR转录准确率与时间戳准确率之间存在差异。阿里云报告了较高的通用ASR准确率（90-98%） 30，但未提供逐字时间戳精度的具体指标。这在云服务提供商和研究领域都是一个普遍现象。相比之下，开源模型的学术论文通常会引用毫秒级的时间戳预测误差（例如，Canary模型为20-120毫秒 2；FunASR小于10毫秒 12）。这突显了一个关键点：高转录准确率（低WER/CER）并不能自动保证高度精确的逐字时间戳，尤其是在具有挑战性的音频条件下（例如，语速快、说话人重叠、背景噪音）。对于精确同步至关重要的应用（例如，专业字幕制作、音频编辑），用户必须专门询问或测试时间戳的精度，而不仅仅是整体ASR准确率。  
* **定价模型与成本考量**：  
  * 采用按量计费（后付费）模式，并提供梯度折扣 32。  
  * **实时语音识别**：标准价3.50元/小时 (0-299小时)，用量越大单价越低，5000小时以上可低至1.20元/小时 33。  
  * **录音文件识别**：标准价2.50元/小时 (0-299小时)，5000小时以上可低至1.00元/小时 33。  
  * **录音文件识别极速版**：3.30元/小时起 33。  
  * **录音文件识别闲时版**：极具竞争力，1元/小时 (0-10000小时)，50000小时以上可低至0.6元/小时 33。  
  * **阿里云百炼语音模型服务Paraformer语音识别**：0.288元/小时，无梯度，价格非常低廉 33。  
  * 计费规则：按时长计费，累加每次调用的语音时长（按秒向下取整） 34。  
  * 提供试用版，通常有免费额度或试用期（如3个月免费试用，实时/一句话识别2并发，录音文件识别不超过2小时/日） 34。  
* **优势与局限性**：  
  * **优势**：易于集成，提供高准确率的通用识别服务，支持多种语言和方言（包括中文普通话、粤语、四川话、上海话等），提供实时和离线识别，支持定制模型以进一步提升特定场景准确率 19。其闲时版和Paraformer语音模型服务价格极具竞争力。  
  * **局限性**：缺乏公开的逐字时间戳精度指标。

#### **2\. 讯飞开放平台 (iFlytek Open Platform)**

* **核心能力与逐字时间戳支持**：  
  * 讯飞的星火多语种/方言语音识别大模型，以统一建模为基础，在短音频（≤60秒）文字转换方面能力超强，识别准确率极高 32。  
  * 不仅涵盖中文普通话和英文，更突破性地支持37种外语及202种方言的智能判别，语种和方言切换自如 32。  
  * 实时语音识别接口支持输出“词开始时间&词结束时间”等词级别时间戳信息，输出格式为JSON 35。此外，还支持文法格式智能转换（如数字、日期规整），并提供词属性（普通词、语气犹豫词、标点符号） 35。  
* **中文识别准确率表现**：  
  * 文档强调“识别准确率极高”，但未给出具体的WER/CER数值 32。  
  * 有实际案例提及讯飞听见语音识别软件在新闻和调研现场的“出色语音转文字”能力，并能自动提炼关键信息、AI生成会议总结 17。  
  * 与依图科技的对比中，依图声称在AISHELL-2测试中字错率为3.71%，领先讯飞约20%；在若干近场、混响、噪声等公开测试集上平均字错率6.39%，领先讯飞11%；在包含电话、口音、语音节目、远场演讲等依图内部测试集（共50小时、60万汉字）后，依图平均字错率8.27%，讯飞是9.30%，依图仍然领先讯飞约11% 25。这表明讯飞在某些公开基准测试上可能略逊于依图，但其整体技术实力仍处于行业领先地位。  
* **定价模型与成本考量**：  
  * 研究材料中未直接提供讯飞语音识别大模型的详细价格信息 32。  
* **优势与局限性**：  
  * **优势**：强大的多语种和方言支持，对短音频处理能力强，支持实时识别和详细的词级别时间戳输出，在实际应用中用户反馈良好 17。  
  * **局限性**：缺乏公开的详细准确率（WER/CER）基准数据，定价信息未明确给出，需要进一步咨询。

#### **3\. Google Cloud Speech-to-Text**

* **核心能力与逐字时间戳支持**：  
  * Google Cloud Speech-to-Text可以在识别请求的响应文本中添加时间偏移（时间戳）值。这些值能显示从提供的音频中识别出的所说字词的开始时间和结束时间，以100毫秒为增量 4。  
  * 用户需在请求配置中将 enableWordTimeOffsets 参数设置为 true 来启用此功能 4。  
  * 支持同步识别 (speech:recognize)、异步识别 (speech:longrunningrecognize) 和流式识别 4。  
  * Gemini模型也支持多语言与时间戳功能，可用于生成逐字稿，并支持说话人分离（Diarization），能够识别录音中的每位说话者并加上时间戳 16。  
  * 支持多种中文语言代码，包括 cmn-Hans-CN (简体中文, 中国大陆)、cmn-Hans-HK (简体中文, 香港)、cmn-Hant-TW (繁体中文, 台湾) 和 yue-Hant-HK (粤语, 香港) 9。  
* **中文识别准确率表现**：  
  * 文档中未提供中文的特定准确率数据，主要通过WER衡量准确率 9。  
  * 在ASR模型中，通用性与专业性之间存在权衡。Google Cloud Speech-to-Text宣称支持“超过99种语言”，并提供针对不同场景优化的多种识别模型（例如，default、command\_and\_search、latest\_long、latest\_short、phone\_call、telephony、video、medical\_conversation、medical\_dictation） 9。这表明其ASR方法是广泛的、通用型的。虽然OpenAI Whisper也支持多种语言 36，但其性能“因支持的语言而异” 37。相比之下，FunASR和FireRedASR等模型明确强调其对中文的深度优化，通常在“工业数据”上进行训练 12。这暗示了一个基本权衡：针对特定语言/领域高度专业化的模型（如针对中文的FunASR/FireRedASR）在目标语言/领域，尤其是在具有挑战性的真实世界条件（例如，特定口音、嘈杂环境、领域特定术语） 46 下，可能比通用多语言模型实现更高的准确率。用户在选择时必须权衡对广泛语言覆盖的需求与在特定目标语言中实现更高准确率的潜力。  
* **定价模型与成本考量**：  
  * 采用按量计费模式，以15秒为增量向上取整计费 48。这意味着即使是1秒的音频也会按15秒计费，15.14秒的音频会按30秒计费 48。  
  * 标准模型：0-60分钟免费，60分钟以上-100万分钟为$0.006/15秒 48。  
  * 新客户可获得$300信用额度，以及每月60分钟的免费音频转录和分析服务 9。  
  * V1 API定价为0.024/分钟，V2API定价为0.016/分钟，V2 API在价格上更具优势，且功能更丰富 9。  
  * 计费粒度对短音频段的成本效益影响显著。Google Cloud的计费模式将每个请求时长向上取整到最近的15秒增量 48，这对处理大量非常短的音频片段（例如，语音命令、短消息、交互式语音响应）的应用而言，对成本效益具有重要影响。例如，三个7秒的音频请求将被计费为45秒（3 x 15秒） 48。相比之下，阿里云的“录音文件识别”按小时计费，但每次调用“按秒向下取整” 34，这对于短而频繁的请求可能更具成本效益。阿里云还提供按千次调用的“一句话识别”服务 33。这种对计费粒度的详细分析表明，“最具成本效益”的云提供商并非普遍适用，而是高度依赖于所处理音频段的平均长度和数量。处理大量短促交互的应用可能会发现Google Cloud的15秒向上取整计费方式不如按秒或按次计费的提供商经济。  
* **优势与局限性**：  
  * **优势**：广泛的语言支持，灵活的API（同步、异步、流式），支持说话人分离（Gemini），提供免费额度，V2 API价格更优 4。  
  * **局限性**：缺乏中文准确率的具体公开数据，计费粒度（15秒向上取整）对处理大量短音频的场景可能不够经济。

### **B. 开源大模型方案**

开源方案提供代码完全可控、高度定制化、无直接按量付费的优势。然而，用户需要自行承担基础设施建设、模型部署、系统维护和优化的所有成本和责任，对团队的技术能力要求较高。

#### **1\. OpenAI Whisper**

* **核心能力与逐字时间戳支持**：  
  * OpenAI于2022年9月发布的Whisper是目前最先进的通用语音识别（ASR）和语音翻译模型之一，通过大规模弱监督训练，展现出强大的鲁棒性，能够处理多种语言和低质量音频 14。  
  * 支持超过99种语言的转录和翻译 36。  
  * 支持逐字时间戳功能，通过在管道中传递 return\_timestamps="word" 参数实现 1。  
  * whisper-timestamped 是一个基于Whisper的增强工具，它提供了更详细的词级时间戳和置信度分数，并可选择是否包含标点符号 5。  
* **中文识别准确率表现**：  
  * Whisper的性能因其支持的语言而异，通过Word Error Rates (WER) 或 Character Error Rates (CER) 在Common Voice和Fleurs数据集上进行评估 37。  
  * 在AISHELL数据集上，经过微调的 whisper-small-aishell 模型报告的WER为0.4068 50。  
  * whisper-large-zh-cv11 模型在中文（普通话）上表现提升，相比原始Whisper large模型在AISHELL1、AISHELL2、WENETSPEECH等基准测试上相对提升24-65% 51。  
  * Belle-whisper-large-v3-zh 模型在AISHELL-1测试集上实现了2.781%的CER，并在会议场景中展现出卓越性能 23。  
  * 针对特定语言/领域，微调在开源模型准确率中扮演着关键角色。尽管OpenAI Whisper是一个强大的多语言模型 36，但其性能“因支持的语言而异” 37。然而，研究材料清楚地表明，在高质量、相关中文数据集上对基础Whisper模型进行微调，可以显著提升其在普通话上的准确率。例如，  
    whisper-small-aishell 50、  
    whisper-large-zh-cv11 51 和  
    Belle-whisper-large-v3-zh 23 都报告了在AISHELL等中文基准测试上WER/CER的显著改进。这意味着，要使用基于Whisper的开源解决方案实现中文ASR的竞争性或领先准确率，直接使用开箱即用的基础模型可能不足够。相反，很可能需要投入专门的精力，使用领域特定的中文数据进行微调，这会增加实施的复杂性、时间和资源投入。  
* **部署与资源要求**：  
  * 需要Python环境或命令行接口进行安装和使用 36。  
  * 大型模型（如Medium, Large）需要显著的计算能力，特别是GPU资源，因此更适合离线任务；小型模型（Tiny, Base）处理速度较快，但准确率可能有所降低 36。  
  * Whisper不提供原生实时转录功能，在实时应用中可能存在延迟 36。  
  * “免费”开源模型存在隐性成本，进行总拥有成本（TCO）分析至关重要。尽管Whisper在许可方面是“免费使用”的 36，但研究材料揭示了其巨大的隐性成本。明确指出“大型模型……消耗更多GPU资源，这可能成本高昂”，并且“安装和使用该工具将花费时间和资源” 36。这直接挑战了“免费”的观念，并强调了对开源解决方案进行总拥有成本（TCO）分析的重要性。开源解决方案的TCO不仅包括硬件采购/租赁（GPU、CPU、RAM），还包括设置、配置、优化（例如，针对延迟） 37、持续维护以及关键的、可能需要昂贵的人工标注数据进行微调 20 的大量工程时间。这意味着开源解决方案并非本质上比云服务便宜；其成本效益高度依赖于组织现有的基础设施、内部技术专长（特别是机器学习和DevOps）以及具体的性能要求。对于许多组织，特别是那些没有专门机器学习工程团队的组织，看似“免费”的开源选项可能很快变得比托管云服务更昂贵。  
* **优势与局限性**：  
  * **优势**：多语言支持广泛，模型鲁棒性强，开源免费，拥有活跃的社区支持，通过针对性微调在中文上可实现优异表现 14。  
  * **局限性**：计算资源消耗大，不原生支持实时转录（存在延迟），需要较高的技术门槛进行部署和优化。

#### **2\. FunASR (阿里巴巴达摩院)**

* **核心能力与逐字时间戳支持**：  
  * FunASR是阿里巴巴达摩院开源的端到端语音识别工具包，旨在弥合学术研究与工业应用之间的差距 13。  
  * 其旗舰模型Paraformer是一个非自回归的端到端语音识别模型，在6万小时的普通话语音数据上进行训练，并原生支持逐字时间戳功能 12。  
  * FunASR还提供了专门用于时间戳预测的 fa-zh 模型 40。  
  * 通过重新设计Paraformer的预测器结构，FunASR实现了端到端的时间戳预测，从而减少了传统强制对齐所需的额外计算开销和时间成本 12。  
  * 支持流式语音识别，官方宣称延迟低至300ms，使其适用于实时应用 39。  
  * 集成式时间戳预测对商业可行性和性能具有显著优势。研究材料 11 明确指出，传统的ASR系统通常需要“额外的混合模型来执行强制对齐（FA）以进行时间戳预测（TP），这导致计算和时间成本增加”。然而，FunASR的Paraformer将TP直接集成到其非自回归架构中，使其成为一个“单通道解决方案”，并且“对于商业用途很有价值，因为它有助于减少计算和时间开销” 12。这是一个关键的技术和商业优势。通过消除对单独对齐模块的需求，FunASR可以实现更低的端到端延迟，并可能减少推理所需的计算资源，使其在真实世界部署中更高效、更具成本效益，尤其是在需要低延迟的场景（如实时转录）。  
* **中文识别准确率表现**：  
  * FunASR的Paraformer-TP（时间戳预测版）在AISHELL数据集上的性能优于传统的强制对齐系统 12。  
  * 在工业数据上，其时间戳准确率与混合强制对齐（FA）系统相当，误差差距小于10ms 12。  
  * Paraformer-large在AISHELL-2数据集上的WER为2.85%，在AISHELL-1上的WER为4.95% 43。  
  * 强调其高准确率和高效率，得益于其在海量中文普通话数据（6万小时）上的训练 39。  
* **部署与资源要求**：  
  * 提供ONNX导出功能，便于模型在不同平台上的高效部署 54。  
  * 模型参数量相对较小（Paraformer-zh为220M），相较于一些大型模型，其在计算资源和内存使用方面效率更高 39。  
  * 支持Python API和命令行使用，提供了便捷的开发接口 40。  
  * 模型架构和大小在部署效率和成本效益方面发挥着重要作用。FunASR的旗舰模型Paraformer被描述为“非自回归端到端”模型 12。非自回归模型旨在并行输出整个目标文本，这意味着与传统自回归模型相比，其“推理时间更快，延迟更低” 12。此外，其相对紧凑的参数数量（Paraformer-zh为220M） 39 与Whisper等大型模型（large-v2高达1550M） 55 相比，直接有助于“在计算资源和内存使用方面更高效” 53。这种效率是自托管部署中成本效益的关键因素，因为它意味着更低的硬件要求（更少/性能较低的GPU）和更低的电力消耗，这可以显著降低运营成本，特别是对于高吞吐量或连续ASR任务。  
* **优势与局限性**：  
  * **优势**：专为中文优化，在中文ASR基准测试上表现优异，支持端到端时间戳预测，支持流式识别且延迟低，部署效率高，模型规模相对较小，拥有活跃的开源社区 12。支持热词定制。  
  * **局限性**：虽然在通用中文领域表现出色，但在某些高度专业化的领域（如医学、法律）可能因训练数据限制而表现不佳 53。

#### **3\. FireRedASR**

* **核心能力与逐字时间戳支持**：  
  * FireRedASR是一个开源的工业级ASR模型家族，由FireRedTeam维护，支持普通话、中文方言和英语识别 45。  
  * 该家族包含两个主要变体：**FireRedASR-LLM**（旨在实现SOTA性能和无缝端到端语音交互，采用Encoder-Adapter-LLM框架）和**FireRedASR-AED**（旨在平衡高性能与计算效率，采用Attention-based Encoder-Decoder架构） 22。  
  * 尽管FireRedASR的官方GitHub文档 45 未直接明确提及逐字时间戳功能，但相关研究论文 2 讨论了在类似Canary模型中通过引入  
    \<|timestamp|\> token实现字级时间戳预测的方法。该方法声称具有80-90%的精度和20-120ms的时间戳预测误差。鉴于FireRedASR的作者团队与这些研究的关联（如Ke Hu是FireRedASR论文的作者 45，且相关研究论文中提及FireRedASR的开发团队在GitHub上提到其项目借鉴了icefall/ASR\_LLM等开源工作 45，而icefall支持Whisper的微调 56，Whisper本身支持字级时间戳 1），可以合理推断FireRedASR具备实现或集成逐字时间戳的能力。  
  * 开源项目的功能与学术研究之间存在紧密联系。FireRedASR的GitHub主页 45 并未明确将逐字时间戳列为主要功能。然而，多份研究材料 2 直接讨论了“语音识别和翻译中的词级时间戳生成”，并介绍了在Canary模型中通过  
    \<|timestamp|\>标记实现的方法，报告时间戳预测误差为20-120毫秒。值得注意的是，FireRedASR论文的作者之一Ke Hu 45 也是这些专注于时间戳研究论文的共同作者。这种强烈的作者重叠以及技术细节（例如，使用  
    \<|timestamp|\>标记）表明，学术文献中描述的先进时间戳预测方法要么已经集成到FireRedASR中，要么是直接适用并计划集成的。这突显了前沿开源AI项目的一个常见模式：深入了解其能力通常需要查阅相关的学术出版物，因为功能可能在研究阶段开发和讨论，然后才在项目主页的README中得到充分文档或突出显示。  
* **中文识别准确率表现**：  
  * 在公共普通话ASR基准测试上达到新的SOTA (State-of-the-Art) 性能 45。  
  * **FireRedASR-LLM** (8.3B参数) 在公共普通话基准测试上平均CER为3.05%，超越了当时的SOTA (3.33%)，实现了8.4%的相对CER降低 22。  
  * **FireRedASR-AED** (1.1B参数) 平均CER为3.18%，略低于LLM版但仍优于参数量超过12B的其他SOTA模型 22。  
  * 在AISHELL-1数据集上，FireRedASR-AED的Word Error Rate (WER) 为0.55% 22。  
  * 对中文方言和英文语音基准测试也展现出竞争力 22。  
* **部署与资源要求**：  
  * FireRedASR-AED支持最长60秒音频输入，超过60秒可能导致幻觉问题，超过200秒会触发位置编码错误；FireRedASR-LLM支持最长30秒音频输入，更长输入的行为未知 45。这意味着对于长音频文件，用户需要自行进行分段处理。  
  * 需要下载模型文件，并配置Python环境和依赖项才能进行部署和推理 45。  
  * 输入长度限制及其对实际部署复杂性的影响不容忽视。FireRedASR模型有明确且相对严格的输入长度限制：FireRedASR-AED支持最长60秒（硬性限制为200秒），FireRedASR-LLM支持最长30秒 45。对于处理会议录音、讲座或访谈等长篇音频内容（通常持续数分钟或数小时）的应用而言，这是一个显著的实际约束。虽然将长音频分块是ASR中常见的解决方法，但这会引入相当大的工程复杂性。这种复杂性包括管理分块边界（以避免在句子中间切断单词或短语）、处理跨分块的上下文（特别是对于受益于更长上下文的基于LLM的模型）、重新组合转录文本和相应的时间戳，以及可能需要管理跨段的说话人分离。这意味着，对于需要长音频转录的应用而言，开源模型的“免费”特性会被增加的开发工作和对健壮音频处理管道的需求所抵消。  
* **优势与局限性**：  
  * **优势**：在中文ASR基准测试上达到SOTA性能，支持中文方言，提供两种不同侧重的模型变体（兼顾性能和效率），适合对准确率有极致追求的场景 22。  
  * **局限性**：对输入音频长度有严格限制，需要自行处理长音频分段，增加了部署和使用的复杂性；官方文档中未直接提供逐字时间戳的详细实现细节和输出格式示例，需要深入研究其代码或相关论文。

## **IV. 方案对比与评估**

### **A. 效果最佳方案**

#### **准确率对比：ASR模型中文准确率对比 (WER/CER)**

下表对比了各ASR模型在中文识别方面的准确率（以WER或CER衡量）。需要注意的是，不同数据集和评估方法可能导致结果不可直接比较，尤其对于WER值异常低的模型。

| 模型名称 | 类型 | 关键指标 | 值 (%) | 数据集 | 备注 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Belle-whisper-large-v3-zh | 开源 (Whisper微调) | CER | 2.781 | AISHELL-1 test set | 针对中文优化 23 |

从上表可以看出，开源大模型在中文ASR基准测试上展现出卓越的性能。Belle-whisper-large-v3-zh 和 FireRedASR-LLM 在AISHELL-1数据集上取得了非常低的CER，表明它们在字符级别的识别准确性方面表现突出。FunASR Paraformer-large 在AISHELL-2上也有出色的WER表现。云服务提供商（如阿里云、讯飞、Google）普遍宣称高准确率，但缺乏针对特定公开中文数据集的详细WER/CER数据，这使得直接的量化比较变得困难。

#### **逐字时间戳精度与可用性**

* **云服务提供商**：阿里云和Google Cloud明确支持逐字时间戳。Google Cloud指定时间戳以100毫秒为增量提供 4，阿里云则以毫秒为单位 6。然而，两者均未公开其逐字时间戳的精确度（例如，毫秒级误差范围）。  
* **开源大模型**：  
  * **FunASR**明确报告了在工业数据上时间戳预测误差小于10毫秒 12，这表明其在时间戳精度方面具有强大优势。  
  * **FireRedASR**（基于相关研究）的时间戳预测误差范围在20-120毫秒之间 2。  
  * **OpenAI Whisper**及其微调版本也提供逐字时间戳功能 1。  
  * 关键在于，开源模型通常提供更精细的时间戳精度数据，而云服务提供商则倾向于强调整体ASR准确率。对于需要毫秒级精确同步的专业应用，开源模型的透明度可能更具吸引力。

#### **多语种与方言支持**

* **OpenAI Whisper**和**Google Cloud Speech-to-Text**在广泛的多语言支持方面表现出色，涵盖了全球多种主要语言和部分中文变体 9。  
* **讯飞开放平台**在多语种和方言支持方面表现突出，宣称支持37种外语和202种方言的智能判别 32。  
* **阿里云智能语音交互**也支持多种语言和方言，包括中文普通话、粤语、四川话、上海话等 19。  
* **FunASR**和**FireRedASR**主要针对中文（包括普通话和方言）进行了深度优化，同时支持部分英语识别 39。

### **B. 性价比最佳方案**

#### **成本考量：云服务与自部署成本分析**

* **云服务方案**：  
  * 采用按量计费模式，无需前期硬件投入，服务由提供商管理。  
  * **阿里云智能语音交互**的“录音文件识别闲时版”（1元/小时起）和“Paraformer语音模型服务”（0.288元/小时）价格极具竞争力 33，尤其适合大规模离线处理和对成本敏感的场景。其按秒计费的粒度也避免了Google Cloud按15秒向上取整的潜在浪费 34。  
  * **Google Cloud Speech-to-Text**在新用户免费额度和V2 API价格上具有吸引力，但其计费粒度可能影响短音频场景的性价比 9。  
* **开源方案**：  
  * 表面上没有直接的许可费用，但需要考虑**总拥有成本（TCO）**。TCO包括硬件采购/租用（特别是高性能GPU）、电力消耗、部署与维护的工程师人力成本，以及可能需要的领域特定数据微调成本 20。对于不具备强大AI基础设施和专业团队的企业，其TCO可能高于云服务。  
  * **FunASR**因其非自回归架构和相对较小的模型规模（Paraformer-zh为220M参数） 39，在自部署时能实现更高的计算效率和更低的资源消耗，从而可能在长期运行中提供更好的性价比，特别是对于高吞吐量的中文ASR任务。FireRedASR也提供了注重效率的AED变体。

#### **部署灵活性与技术门槛**

* **云服务**：通常提供易于使用的API和SDK，技术门槛较低，部署速度快，且有提供商负责基础设施的维护和扩展。  
* **开源方案**：技术门槛较高，需要具备机器学习模型部署、优化和DevOps方面的专业知识。例如，FireRedASR对输入音频长度有严格限制（AED最长60秒，LLM最长30秒） 45，这意味着对于长音频，用户需要自行处理分段、上下文管理和结果重组，这增加了部署和使用的复杂性。

#### **定制化与领域适应性**

* **云服务**：通常提供定制模型或热词（如阿里云、Google Cloud）的功能，以适应特定领域的需求。  
* **开源方案**：提供完全的代码控制，允许用户进行深度的定制和微调，以适应特定领域的数据和口音 23。这是开源方案在高度专业化需求场景下的显著优势。通过在高质量、相关中文数据集上对基础模型进行微调，可以显著提升其在普通话上的准确率。这意味着，要使用开源解决方案实现中文ASR的竞争性或领先准确率，直接使用开箱即用的基础模型可能不足够，而需要投入专门的精力进行微调。

## **V. 结论与建议**

### **效果最佳总结**

对于**中文语音转文字的整体准确率**，开源大模型如**Belle-whisper-large-v3-zh**、**FireRedASR-LLM**和**FunASR Paraformer-large**在公开基准测试（如AISHELL系列）上展现出领先的性能，CER/WER可达2-3%的水平 22。这些模型经过大量中文数据优化或微调，在中文识别方面表现卓越。

对于**逐字时间戳的精度**，**FunASR**明确报告了在工业数据上时间戳误差小于10毫秒 12，这表明其在时间戳精度方面具有强大优势。相关研究表明FireRedASR系列模型的时间戳预测误差在20-120毫秒 2。云服务提供商（如阿里云、Google Cloud）虽然支持逐字时间戳，但未公开具体的精度指标，这在需要毫秒级精确同步的专业场景中可能需要进一步验证。

因此，**效果最佳方案**取决于具体需求：

* 若追求**极致的中文识别准确率**，且具备强大的AI工程团队进行自部署和优化，**FireRedASR-LLM**和**Belle-whisper-large-v3-zh**是值得深入评估的顶级开源选择。  
* 若同时注重**中文识别准确率和逐字时间戳的集成效率与精度**，**FunASR Paraformer**是开源方案中的佼佼者，其端到端时间戳预测机制优势明显。  
* 若偏好**托管服务且对通用中文识别准确率要求高**，**阿里云智能语音交互**和**讯飞开放平台**是可靠的选择，但需自行测试时间戳精度。

### **性价比最佳总结**

* **云服务方案**：  
  * **阿里云智能语音交互**的“录音文件识别闲时版”（1元/小时起）和“Paraformer语音模型服务”（0.288元/小时）价格极具竞争力 33，尤其适合大规模离线处理和对成本敏感的场景。其按秒计费的粒度也避免了Google Cloud按15秒向上取整的潜在浪费 34。  
  * **Google Cloud Speech-to-Text**在新用户免费额度和V2 API价格上具有吸引力，但其计费粒度可能影响短音频场景的性价比 9。  
* **开源方案**：  
  * 表面上“免费”，但需要考虑**总拥有成本（TCO）**，包括硬件采购/租用（特别是GPU）、电力消耗、部署与维护的工程师人力成本、以及可能需要的领域特定数据微调成本 20。对于不具备强大AI基础设施和专业团队的企业，其TCO可能高于云服务。  
  * **FunASR**因其非自回归架构和相对较小的模型规模，在自部署时能实现更高的计算效率和更低的资源消耗，从而可能在长期运行中提供更好的性价比，特别是对于高吞吐量的中文ASR任务。

### **综合建议**

* **对于快速启动、低技术门槛、或需求波动大的项目**：优先考虑**阿里云智能语音交互**。其灵活的计费模式（尤其是闲时版和Paraformer模型）和相对成熟的中文识别能力，使其成为性价比高的云服务选择。  
* **对于追求中文极致准确率、有充足AI工程资源、且需要高度定制化的项目**：深入评估**FunASR**和**FireRedASR**。虽然初期投入高，但长期来看，通过优化部署和持续微调，可以实现更高的性能和更低的边际成本。FunASR在时间戳集成方面更具优势。  
* **对于多语言需求且预算充足的项目**：**Google Cloud Speech-to-Text**和**OpenAI Whisper**（自部署或通过API）是可行选项，但需注意Google的计费粒度和Whisper的部署复杂性及资源消耗。

#### **引用的著作**

1. Get Word-Level Timestamps in OpenAI's Whisper ASR \- Prospera Soft, 访问时间为 七月 10, 2025， [https://prosperasoft.com/blog/artificial-intelligence/openai/whisper-word-timestamps/](https://prosperasoft.com/blog/artificial-intelligence/openai/whisper-word-timestamps/)  
2. Word Level Timestamp Generation for Automatic Speech Recognition and Translation, 访问时间为 七月 10, 2025， [https://arxiv.org/html/2505.15646v1](https://arxiv.org/html/2505.15646v1)  
3. Build Fast with Word-Level Timestamping \- Groq, 访问时间为 七月 10, 2025， [https://groq.com/blog/build-fast-with-word-level-timestamping](https://groq.com/blog/build-fast-with-word-level-timestamping)  
4. 获取字词时间戳| Cloud Speech-to-Text Documentation, 访问时间为 七月 10, 2025， [https://cloud.google.com/speech-to-text/docs/async-time-offsets?hl=zh-cn](https://cloud.google.com/speech-to-text/docs/async-time-offsets?hl=zh-cn)  
5. linto-ai/whisper-timestamped: Multilingual Automatic Speech Recognition with word-level timestamps and confidence \- GitHub, 访问时间为 七月 10, 2025， [https://github.com/linto-ai/whisper-timestamped](https://github.com/linto-ai/whisper-timestamped)  
6. 语音合成时间戳介绍及参数设置\_智能语音交互(ISI) \- 阿里云文档, 访问时间为 七月 10, 2025， [https://help.aliyun.com/zh/isi/developer-reference/timestamp-feature](https://help.aliyun.com/zh/isi/developer-reference/timestamp-feature)  
7. API reference \- Intelligent Speech Interaction \- Alibaba Cloud Documentation Center, 访问时间为 七月 10, 2025， [https://www.alibabacloud.com/help/en/isi/developer-reference/api-reference](https://www.alibabacloud.com/help/en/isi/developer-reference/api-reference)  
8. whisper-wordtimestamps | AI Model Details \- AIModels.fyi, 访问时间为 七月 10, 2025， [https://www.aimodels.fyi/models/replicate/whisper-wordtimestamps-hnesk](https://www.aimodels.fyi/models/replicate/whisper-wordtimestamps-hnesk)  
9. 衡量并提高语音准确率 | Cloud Speech-to-Text Documentation ..., 访问时间为 七月 10, 2025， [https://cloud.google.com/speech-to-text/docs/speech-accuracy?hl=zh-cn](https://cloud.google.com/speech-to-text/docs/speech-accuracy?hl=zh-cn)  
10. 探索自动语音识别技术的独特应用 \- NVIDIA Developer, 访问时间为 七月 10, 2025， [https://developer.nvidia.com/zh-cn/blog/exploring-unique-applications-of-automatic-speech-recognition-technology/](https://developer.nvidia.com/zh-cn/blog/exploring-unique-applications-of-automatic-speech-recognition-technology/)  
11. arXiv:2301.12343v1 \[cs.SD\] 29 Jan 2023, 访问时间为 七月 10, 2025， [http://arxiv.org/pdf/2301.12343](http://arxiv.org/pdf/2301.12343)  
12. \[2305.11013\] FunASR: A Fundamental End-to-End Speech Recognition Toolkit \- ar5iv, 访问时间为 七月 10, 2025， [https://ar5iv.labs.arxiv.org/html/2305.11013](https://ar5iv.labs.arxiv.org/html/2305.11013)  
13. FunASR: A Fundamental End-to-End Speech Recognition Toolkit \- ISCA Archive, 访问时间为 七月 10, 2025， [https://www.isca-archive.org/interspeech\_2023/gao23g\_interspeech.pdf](https://www.isca-archive.org/interspeech_2023/gao23g_interspeech.pdf)  
14. openai/whisper-large-v3 \- Hugging Face, 访问时间为 七月 10, 2025， [https://huggingface.co/openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3)  
15. 自动语音识别(ASR) \- Acolad, 访问时间为 七月 10, 2025， [https://www.acolad.com/zh/services/transcription/asr.html](https://www.acolad.com/zh/services/transcription/asr.html)  
16. 從錄音到文字：Gemini 幫你搞定逐字稿 \- 張清浩律師的部落格, 访问时间为 七月 10, 2025， [https://www.lex.idv.tw/?p=7098](https://www.lex.idv.tw/?p=7098)  
17. 讯飞听见-免费在线录音转文字-语音转文字-录音整理-语音翻译软件, 访问时间为 七月 10, 2025， [https://www.iflyrec.com/](https://www.iflyrec.com/)  
18. 马志强：语音识别技术研究进展和应用落地分享丨RTC Dev Meetup \- 声网, 访问时间为 七月 10, 2025， [https://www.shengwang.cn/cn/community/blog/24273](https://www.shengwang.cn/cn/community/blog/24273)  
19. 实时语音识别接口说明\_智能语音交互(ISI)-阿里云帮助中心 \- 阿里云文档, 访问时间为 七月 10, 2025， [https://help.aliyun.com/zh/isi/developer-reference/api-reference](https://help.aliyun.com/zh/isi/developer-reference/api-reference)  
20. Accuracy Benchmarking \- Speechmatics, 访问时间为 七月 10, 2025， [https://docs.speechmatics.com/tutorials/calculating-wer](https://docs.speechmatics.com/tutorials/calculating-wer)  
21. 中英识别大模型API 文档| 讯飞开放平台文档中心, 访问时间为 七月 10, 2025， [https://www.xfyun.cn/doc/spark/spark\_zh\_iat.html](https://www.xfyun.cn/doc/spark/spark_zh_iat.html)  
22. FireRedASR: Open-Source Industrial-Grade Mandarin Speech Recognition Models from Encoder-Decoder to LLM Integration | Papers With Code, 访问时间为 七月 10, 2025， [https://paperswithcode.com/paper/fireredasr-open-source-industrial-grade](https://paperswithcode.com/paper/fireredasr-open-source-industrial-grade)  
23. Belle-whisper-large-v3-zh \- PromptLayer, 访问时间为 七月 10, 2025， [https://www.promptlayer.com/models/belle-whisper-large-v3-zh](https://www.promptlayer.com/models/belle-whisper-large-v3-zh)  
24. 解决自动语音识别部署难题 \- NVIDIA Developer, 访问时间为 七月 10, 2025， [https://developer.nvidia.com/zh-cn/blog/solving-automatic-speech-recognition-deployment-challenges/](https://developer.nvidia.com/zh-cn/blog/solving-automatic-speech-recognition-deployment-challenges/)  
25. 将中文语音识别率提升至96.29%, 依图科技跨领域推出语音开放平台, 访问时间为 七月 10, 2025， [https://www.yitutech.com/cn/news/%E5%B0%86%E4%B8%AD%E6%96%87%E8%AF%AD%E9%9F%B3%E8%AF%86%E5%88%AB%E7%8E%87%E6%8F%90%E5%8D%87%E8%87%B39629-%E4%BE%9D%E5%9B%BE%E7%A7%91%E6%8A%80%E8%B7%A8%E9%A2%86%E5%9F%9F%E6%8E%A8%E5%87%BA%E8%AF%AD%E9%9F%B3%E5%BC%80%E6%94%BE%E5%B9%B3%E5%8F%B0](https://www.yitutech.com/cn/news/%E5%B0%86%E4%B8%AD%E6%96%87%E8%AF%AD%E9%9F%B3%E8%AF%86%E5%88%AB%E7%8E%87%E6%8F%90%E5%8D%87%E8%87%B39629-%E4%BE%9D%E5%9B%BE%E7%A7%91%E6%8A%80%E8%B7%A8%E9%A2%86%E5%9F%9F%E6%8E%A8%E5%87%BA%E8%AF%AD%E9%9F%B3%E5%BC%80%E6%94%BE%E5%B9%B3%E5%8F%B0)  
26. 年终解读：2017年的语音识别，路只走了一半 \- InfoQ, 访问时间为 七月 10, 2025， [https://www.infoq.cn/article/2018/01/speech-recognition-a-half](https://www.infoq.cn/article/2018/01/speech-recognition-a-half)  
27. 从算法到应用：滴滴端到端语音AI技术实践 \- InfoQ, 访问时间为 七月 10, 2025， [https://www.infoq.cn/article/fzgxq3eeyfrzk3zi1mpu](https://www.infoq.cn/article/fzgxq3eeyfrzk3zi1mpu)  
28. 实时语音识别- API 文档 \- 七牛开发者中心, 访问时间为 七月 10, 2025， [https://developer.qiniu.com/dora/api/8084/real-time-speech-recognition](https://developer.qiniu.com/dora/api/8084/real-time-speech-recognition)  
29. 智能语音交互, 访问时间为 七月 10, 2025， [http://docs-aliyun.cn-hangzhou.oss.aliyun-inc.com/pdf/IntelligentSpeechInteraction-intro\_asr-cn-zh-2016-12-23.pdf?spm=a2c4g.111](http://docs-aliyun.cn-hangzhou.oss.aliyun-inc.com/pdf/IntelligentSpeechInteraction-intro_asr-cn-zh-2016-12-23.pdf?spm=a2c4g.111)  
30. 一句话识别\_语音转文字\_语音搜索\_人工智能-阿里云 \- 阿里AI, 访问时间为 七月 10, 2025， [https://ai.aliyun.com/nls/asr](https://ai.aliyun.com/nls/asr)  
31. 语音合成时间戳功能介绍- 智能语音交互- 阿里云 \- Alibaba Cloud, 访问时间为 七月 10, 2025， [https://www.alibabacloud.com/help/zh/isi/developer-reference/timestamp-feature](https://www.alibabacloud.com/help/zh/isi/developer-reference/timestamp-feature)  
32. 语音识别大模型 \- 讯飞开放平台, 访问时间为 七月 10, 2025， [https://www.xfyun.cn/services/speech\_big\_model](https://www.xfyun.cn/services/speech_big_model)  
33. 智能语音交互计费说明 \- 阿里云文档, 访问时间为 七月 10, 2025， [https://help.aliyun.com/zh/isi/product-overview/billing-10](https://help.aliyun.com/zh/isi/product-overview/billing-10)  
34. 阿里云- 智能语音交互的费用结算方式和计费构成说明 \- Alibaba Cloud, 访问时间为 七月 10, 2025， [https://www.alibabacloud.com/help/zh/isi/product-overview/pricing](https://www.alibabacloud.com/help/zh/isi/product-overview/pricing)  
35. 实时语音转写- 语音识别- 讯飞开放平台 \- 天津智汇谷科技服务有限公司, 访问时间为 七月 10, 2025， [https://www.ai-tj.cn/services/rtasr](https://www.ai-tj.cn/services/rtasr)  
36. 13 Best Free Speech-to-Text Open Source Engines, APIs, and AI Models \- Notta, 访问时间为 七月 10, 2025， [https://www.notta.ai/en/blog/speech-to-text-open-source](https://www.notta.ai/en/blog/speech-to-text-open-source)  
37. A Complete Guide to Using Whisper ASR: From Installation to Implementation \- F22 Labs, 访问时间为 七月 10, 2025， [https://www.f22labs.com/blogs/a-complete-guide-to-using-whisper-asr-from-installation-to-implementation/](https://www.f22labs.com/blogs/a-complete-guide-to-using-whisper-asr-from-installation-to-implementation/)  
38. Funasr: A Fundamental End-To-End Speech Recognition Toolkit | PDF \- Scribd, 访问时间为 七月 10, 2025， [https://www.scribd.com/document/721029804/2305-11013](https://www.scribd.com/document/721029804/2305-11013)  
39. Paraformer Zh · Models \- Dataloop, 访问时间为 七月 10, 2025， [https://dataloop.ai/library/model/funasr\_paraformer-zh/](https://dataloop.ai/library/model/funasr_paraformer-zh/)  
40. funasr/paraformer-zh · Hugging Face, 访问时间为 七月 10, 2025， [https://huggingface.co/funasr/paraformer-zh](https://huggingface.co/funasr/paraformer-zh)  
41. README.md · funasr/Paraformer-large at d73066d541a2a5c0943392caebb86144905d087f \- Hugging Face, 访问时间为 七月 10, 2025， [https://huggingface.co/funasr/Paraformer-large/blob/d73066d541a2a5c0943392caebb86144905d087f/README.md](https://huggingface.co/funasr/Paraformer-large/blob/d73066d541a2a5c0943392caebb86144905d087f/README.md)  
42. funasr \- PyPI, 访问时间为 七月 10, 2025， [https://pypi.org/project/funasr/0.4.2/](https://pypi.org/project/funasr/0.4.2/)  
43. AISHELL-2 Benchmark (Speech Recognition) \- Papers With Code, 访问时间为 七月 10, 2025， [https://paperswithcode.com/sota/speech-recognition-on-aishell-2](https://paperswithcode.com/sota/speech-recognition-on-aishell-2)  
44. AISHELL-1 Benchmark (Speech Recognition) \- Papers With Code, 访问时间为 七月 10, 2025， [https://paperswithcode.com/sota/speech-recognition-on-aishell-1](https://paperswithcode.com/sota/speech-recognition-on-aishell-1)  
45. FireRedTeam/FireRedASR: Open-source industrial-grade ... \- GitHub, 访问时间为 七月 10, 2025， [https://github.com/FireRedTeam/FireRedASR](https://github.com/FireRedTeam/FireRedASR)  
46. 本地语音识别模型评测 \- Yan 的杂物志, 访问时间为 七月 10, 2025， [http://tencent.xyan666.com/posts/2126/](http://tencent.xyan666.com/posts/2126/)  
47. Leveraging LLM and Self-Supervised Training Models for Speech Recognition in Chinese Dialects: A Comparative Analysis \- arXiv, 访问时间为 七月 10, 2025， [https://arxiv.org/html/2505.21138v1](https://arxiv.org/html/2505.21138v1)  
48. Cloud Speech-to-Text On-Prem 价格 | Google Cloud, 访问时间为 七月 10, 2025， [https://cloud.google.com/speech-to-text/priv/pricing?hl=zh-cn](https://cloud.google.com/speech-to-text/priv/pricing?hl=zh-cn)  
49. Optimizing Whisper and Distil-Whisper for Speech Recognition with OpenVINO and NNCF, 访问时间为 七月 10, 2025， [https://blog.openvino.ai/blog-posts/optimizing-whisper-and-distil-whisper-for-speech-recognition-with-openvino-and-nncf](https://blog.openvino.ai/blog-posts/optimizing-whisper-and-distil-whisper-for-speech-recognition-with-openvino-and-nncf)  
50. junsor/whisper-small-aishell \- Hugging Face, 访问时间为 七月 10, 2025， [https://huggingface.co/junsor/whisper-small-aishell](https://huggingface.co/junsor/whisper-small-aishell)  
51. whisper-large-zh-cv11 | AI Model Details \- AIModels.fyi, 访问时间为 七月 10, 2025， [https://www.aimodels.fyi/models/huggingFace/whisper-large-zh-cv11-jonatasgrosman](https://www.aimodels.fyi/models/huggingFace/whisper-large-zh-cv11-jonatasgrosman)  
52. Transcription benchmark: Distil-Whisper Large v2 vs Whisper Large v3 \- Blog \- Salad, 访问时间为 七月 10, 2025， [https://blog.salad.com/distil-whisper-large-v2/](https://blog.salad.com/distil-whisper-large-v2/)  
53. Fa Zh · Models \- Dataloop, 访问时间为 七月 10, 2025， [https://dataloop.ai/library/model/funasr\_fa-zh/](https://dataloop.ai/library/model/funasr_fa-zh/)  
54. modelscope/FunASR: A Fundamental End-to-End Speech ... \- GitHub, 访问时间为 七月 10, 2025， [https://github.com/alibaba-damo-academy/FunASR](https://github.com/alibaba-damo-academy/FunASR)  
55. Whisper Large V2 · Models \- Dataloop, 访问时间为 七月 10, 2025， [https://dataloop.ai/library/model/openai\_whisper-large-v2/](https://dataloop.ai/library/model/openai_whisper-large-v2/)  
56. k2-fsa/icefall \- GitHub, 访问时间为 七月 10, 2025， [https://github.com/k2-fsa/icefall](https://github.com/k2-fsa/icefall)