# Prompt Archive 024: Layout Planning Agent

## Purpose

이번 prompt는 LayoutAgent를 keyword generator에서 composition planning agent로 발전시키기 위한 architecture prompt다.

## Summary

LayoutAgent는 layout type, aspect ratio, frame structure, camera view, subject placement, background style, composition rules를 포함한 plan을 만들고 PromptAssembler가 이를 generation prompt로 변환한다.

## Prompt Engineering Note

Visual layout은 단순 keyword가 아니라 camera, frame, placement, negative space 같은 구조적 지시로 표현되어야 한다.
