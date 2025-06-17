#!/bin/bash
set -e

# 1. IAM Policy JSON 파일 생성
cat > s3-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::bgm-selector-bucket/*",
        "arn:aws:s3:::bgm-selector-bucket"
      ]
    }
  ]
}
EOF
echo "s3-policy.json 생성 완료."

# 2. EC2 Trust Policy JSON 파일 생성
cat > ec2-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": { "Service": "ec2.amazonaws.com" },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
echo "ec2-trust-policy.json 생성 완료."

# 3. IAM 역할 생성
echo "IAM 역할 (ssupeaker-ec2-s3-access-role) 생성 중..."
aws iam create-role \
    --role-name ssupeaker-ec2-s3-access-role \
    --assume-role-policy-document file://ec2-trust-policy.json > /dev/null
echo "IAM 역할 생성 완료."

# 4. IAM 정책 생성 및 ARN 추출
echo "IAM 정책 (ssupeaker-s3-read-policy) 생성 중..."
POLICY_ARN=$(aws iam create-policy \
    --policy-name ssupeaker-s3-read-policy \
    --policy-document file://s3-policy.json \
    --query 'Policy.Arn' --output text)
echo "IAM 정책 생성 완료. ARN: $POLICY_ARN"

# 5. 역할에 정책 연결
echo "역할에 정책 연결 중..."
aws iam attach-role-policy \
    --role-name ssupeaker-ec2-s3-access-role \
    --policy-arn "$POLICY_ARN"
echo "정책 연결 완료."

# 6. 임시 파일 정리
rm s3-policy.json ec2-trust-policy.json
echo "임시 JSON 파일 삭제 완료."

echo "모든 AWS IAM 리소스 설정이 성공적으로 완료되었습니다." 