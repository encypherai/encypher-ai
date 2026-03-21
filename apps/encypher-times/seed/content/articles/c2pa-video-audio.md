The Coalition for Content Provenance and Authenticity released version 2.3 of its technical specification on Tuesday, adding comprehensive support for video and audio content signing -- a significant expansion that brings the standard beyond its origins in still image verification.

The updated specification introduces two key capabilities: segment-by-segment signing for live video streams and full-file signing for pre-recorded audio and video content. Both approaches embed C2PA manifests directly into the media container format, ensuring that provenance metadata travels with the content rather than being stored in easily stripped external fields.

For live streaming, the specification defines a protocol in which each segment of a CMAF (Common Media Application Format) stream receives its own signed manifest, with cryptographic chaining between segments to prevent insertion or removal of content. A Merkle tree structure provides efficient verification of the complete stream after broadcast.

"Live video has been the hardest problem in content provenance," said Dr. Leonard Rosenthol. "You can't sign a file that hasn't finished being created yet. The segment-chaining approach in 2.3 solves this elegantly -- each piece is signed as it's produced, and the chain proves nothing was tampered with after the fact."

For publishers, the practical implications are significant. Podcast producers can now sign episodes at export time, ensuring that listeners can verify the audio hasn't been manipulated. News organizations broadcasting live events can sign the stream in real time, providing a cryptographic record that the footage is authentic.

The audio signing capability supports WAV, MP3, and AAC formats. Video signing supports MP4, MOV, and AVI containers. In both cases, the signed manifest includes the creator's identity, the timestamp of signing, and a tamper-evident hash of the content.

Several media companies have already begun implementing the new capabilities. Encypher, which provides enterprise content signing infrastructure, announced same-day support for the 2.3 specification, including an API that allows publishers to sign audio and video files with a single API call.

Industry adoption is expected to accelerate as major content delivery networks add C2PA verification to their distribution pipelines, enabling automatic provenance checking at the point of consumption.
