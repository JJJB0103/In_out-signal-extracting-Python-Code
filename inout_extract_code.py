import pandas as pd
import re

def evaluate_expression(expr):
    """계산식을 평가하고 정수 결과를 반환합니다."""
    try:
        # eval을 사용하여 표현식 계산
        result = eval(expr)
        # 결과가 float인 경우 int로 변환 (소수점 버림)
        return int(result) if isinstance(result, float) else result
    except Exception as e:
        print(f"Expression evaluation error: {e}")
        return None

def parse_parameters_and_signals(file_path):
    parameters = {}
    in_signals = []
    out_signals = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    for line in lines:
        # 파라미터 파싱
        param_match = re.match(r'\s*parameter\s+(\w+)\s+=\s+(.*?),', line)
        if param_match:
            param_name, param_value = param_match.groups()
            evaluated_value = evaluate_expression(param_value.replace("32'd", ""))
            parameters[param_name] = evaluated_value

        # 신호 파싱 및 분류
        signal_match = re.match(r'\s*(output|input)\s+(wire|reg)\s*(\[.*?\])?\s*(\w+)\s*[,;]', line)
        if signal_match:
            direction, signal_type, bit_range, signal_name = signal_match.groups()
            bit_definitions = []
            if bit_range:
                # 대괄호 []가 있는 경우
                bit_ranges = re.findall(r'\[(.*?)\]', bit_range)
                for br in bit_ranges:
                    for param_name, param_value in parameters.items():
                        br = br.replace(param_name, str(param_value))
                    # 비트 범위 연산을 수행하고 '..'으로 범위를 나타냄
                    if ':' in br:  # start:end 형태
                        start, end = br.split(':')
                        start = evaluate_expression(start)
                        end = evaluate_expression(end)
                        if start is not None and end is not None and start - end + 1 != 1:
                            bit_definitions.append(f"[{start}..{end}]")
                    else:  # 단일 숫자 형태
                        size = evaluate_expression(br)
                        if size is not None and size != 1:
                            bit_definitions.append(f"[{size}]")
            full_signal_name = f"{signal_name} {' '.join(bit_definitions)}"
            # 방향에 따라 입력/출력 신호 리스트에 추가
            if direction == 'input':
                in_signals.append(full_signal_name)
            else:
                out_signals.append(full_signal_name)
    
    return in_signals, out_signals

def save_to_csv(in_signals, out_signals, csv_file_path):
    max_length = max(len(in_signals), len(out_signals))
    # 입력과 출력 신호 리스트를 동일한 길이로 패딩
    in_signals.extend([''] * (max_length - len(in_signals)))
    out_signals.extend([''] * (max_length - len(out_signals)))
    df = pd.DataFrame({'In Signals': in_signals, 'Out Signals': out_signals})
    df.to_csv(csv_file_path, index=False)

# 텍스트 파일 경로와 CSV 파일 경로 설정
text_file_path = 'DQ_signals.txt'
csv_file_path = 'DQ_signals.csv'

# 파싱 및 CSV 저장
in_signals, out_signals = parse_parameters_and_signals(text_file_path)
save_to_csv(in_signals, out_signals, csv_file_path)

print(f'CSV 파일이 생성되었습니다: {csv_file_path}')
