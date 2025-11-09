# Use AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies for LaTeX
# Using Amazon Linux 2 package manager
RUN yum update -y && \
    yum install -y \
    texlive \
    texlive-latex \
    texlive-collection-latexrecommended \
    texlive-collection-latexextra \
    && yum clean all && \
    rm -rf /var/cache/yum

# Verify pdflatex installation
# RUN which pdflatex && pdflatex --version

# Copy Python requirements and install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the dailyoffice package (copied into build context by build script)
COPY dailyoffice ${LAMBDA_TASK_ROOT}/dailyoffice/

# Copy the Lambda handler
COPY handler.py ${LAMBDA_TASK_ROOT}/

# Set the Lambda handler
CMD ["handler.lambda_handler"]
