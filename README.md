# Tangut Tools: Utilities and Libraries for Tangut Studies / 西夏文研究软件工具和函数库

[English](#english) | [简体中文](#chinese)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data License: Limited Public Use](https://img.shields.io/badge/Data%20License-Limited%20Public%20Use-blue.svg)](LICENSE-DATA.md)


![Tangut Tool Screenshot](tangut-tool/screenshot.png)

## <a name="english"></a> Overview

This repository offers standalone tools and libraries for the study of the Tangut language, script, and text corpus. Developed by Xun Gong (University of Vienna) and collaborators, it includes:

*   **TgtOrtho - Tangut Orthography Library:** A Python library using finite state transducers (FSTs) to process various Latin-script Tangut transcription systems and their phonological representations. [Learn more](tgtortho/README.md)
*   **"Tangut Tool" GUI (Python/GTK4):** A prototype graphical user interface for dynamic transcription and glossing of Tangut text. [Learn more](tangut-tool/README.md)

The following components are currently being cleaned up for publishing:

*   ~~**Proof-of-Concept Phonological Reconstruction Tool:**~~ An experimental tool for reconstructing Tangut phonology based on the internal structure of *Sea of Characters*.

## **Licensing**  

- **Code:** The code in this repository is licensed under the **MIT License**. You are free to use, modify, and distribute it, provided that you include the original copyright notice.  

- **Data:** The data in this repository is provisionally provided under a **Limited Public Use** license. See [LICENSE-DATA.md](LICENSE-DATA.md) for full details. Key terms:  

  - **Free for Research, Teaching, Publication, and Commercial Use** – You may use and cite **individual** data points in academic research, teaching, and publications, whether in a personal, educational, or business setting. **Internal bulk processing is permitted** as long as the processed results are **not publicly distributed at scale**.

* **Contact:** Please contact Xun Gong (xun.gong@univie.ac.at) for licencing permission.

## Contributing

Contributions and feedback are very welcome\!  We encourage participation from the research community.

**Ways to Contribute:**

  * **Bug Reports:**  If you find any bugs, please open an issue on the GitHub repository.
  * **Feature Requests:**  Suggest new features or improvements by opening an issue.
  * **Code Contributions:**
    1.  Fork the repository.
    2.  Create a new branch for your changes (e.g., `git checkout -b feature/new-functionality`).
    3.  Commit your changes with clear and descriptive commit messages.
    4.  Open a pull request, explaining your modifications.
  * **Data Corrections:** If you find errors or inconsistencies in the data, please open an issue or submit a pull request with corrections.

## Contact

For questions, permission requests, or collaboration opportunities, please contact:

  * **Xun Gong**
  * **University of Vienna**
  * **Email:** xun.gong@univie.ac.at


## <a name="chinese"></a> 概述

本GitHub仓库提供西夏语言、文字及文本研究相关的软件工具和函数库，由龚勋（维也纳大学）及合作者开发，目前包含以下部分：

- **TgtOrtho - 西夏文拟音处理库**
基于有限状态转换器（FST）的Python库，用于西夏文拟音不同拉丁转写系统与音系表示之间的互转。 [详见](tgtortho/README.md)

- **“Tangut Tool” — 西夏文本标注工具**  
  利用 Python/GTK4 开发的原型系统，支持图形界面中的西夏文本的自动标音与语义标注。[详见](tangut-tool/README.md)

以下部分正在紧急整理中，尚未发布：

- ~~**音韵构拟工具**~~  
  基于《文海》的结构特征开发的透明、可解释音韵构拟工具，目前处于试验阶段。

## 授权

- **代码部分**：本仓库所包含代码采用 **MIT 许可证** 开源。您可以可自由调用、二次开发、集成至其他项目等，但需保留版权声明。

- **数据部分**：本仓库所包含的数据现阶段暂时按照 **受限公共使用许可协议** 公开，完整条款详见 [LICENSE-DATA.md](LICENSE-DATA.md) ，主要规定如下：
  - **研究、教学、出版及商业应用均可免费使用**：学术研究、教学、出版及商业场景下的 **具体数据** 引用与使用。**允许内部批量处理**，但请确保处理结果不得整体性公开传播。
  - 如需进一步使用许可，请联系龚勋（xun.gong@univie.ac.at）。

## 协作流程

欢迎广大爱好者朋友与学界同仁通过以下方式参与项目共建：
- **问题反馈**：如发现任何问题，请在 GitHub 上提交 issue。
- **功能建议**：如有新功能讨论，欢迎提出 issue。
- **功能开发**：
  1. Fork 本项目；  
  2. 创建新分支进行开发（例如：`git checkout -b feature/new-functionality`）；  
  3. 编写清晰明了的 commit 说明；  
  4. 发起 pull request，说明您的修改内容。
- **数据校订**：如发现数据错误或其他问题，欢迎提交 issue 或直接通过 pull request 提交修正方案。

## 联系方式

如需咨询授权事宜、学术合作或提供建议，请联系：
- **龚勋**  
- **维也纳大学**  
- **邮箱**：xun.gong@univie.ac.at
