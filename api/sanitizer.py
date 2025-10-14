import re
import sqlparse
from typing import List

# Keywords that mark a COMPLEX, COMPOUND statement (PL/SQL blocks and procedure-like objects).
# These statements are assumed to contain internal semicolons that should NOT trigger a split.
BLOCK_STARTERS = (
    'CREATE OR REPLACE', 'BEGIN', 'DECLARE', 'CREATE PACKAGE', 
    'CREATE FUNCTION', 'CREATE PROCEDURE', 'CREATE TRIGGER'
)

# Commands that are SIMPLE and must be split by semicolon if there are multiple.
# We explicitly check for these when deciding whether to run sqlparse.split.
SPLITTABLE_COMMANDS = (
    'GRANT', 'SET', 'DROP TABLE', 'DROP FUNCTION', 'DROP PROCEDURE', 'INSERT',
    'CREATE TABLE', 'ALTER TABLE', 'CREATE INDEX', 'DROP INDEX', 'CREATE SEQUENCE',
    'DROP SEQUENCE', 'CREATE USER', 'ALTER SESSION'
)


def sanitize_for_execution(sql_content: str, job_type: str) -> List[str]:
    """
    Sanitizes and splits SQL content into executable statements, focusing on Oracle
    syntax by prioritizing the block delimiter ('/') and using a strict keyword-based
    classification to prevent over-splitting internal PL/SQL and compound blocks.
    """
    
    # 1. Primary Split by the Oracle Block Delimiter ('/')
    # This regex is the most critical step and isolates all PL/SQL blocks that end with /.
    blocks_by_slash = re.split(r'^\s*/\s*$', sql_content, flags=re.MULTILINE | re.IGNORECASE)
    
    sanitized_statements = []
    
    for block in blocks_by_slash:
        # 2. Clean the block: remove comments and surrounding whitespace
        cleaned_block = sqlparse.format(
            block,
            strip_comments=True,
            reindent=False
        ).strip()
        
        if not cleaned_block:
            continue
            
        cleaned_block_upper = cleaned_block.upper()
        
        # 3. Check for COMPLEX blocks (PL/SQL, DDL) to KEEP WHOLE
        is_complex_block = False
        for keyword in BLOCK_STARTERS:
            if cleaned_block_upper.startswith(keyword):
                is_complex_block = True
                break
        
        # If it's a complex block (like CREATE FUNCTION or DECLARE/BEGIN)
        # AND it doesn't start with a simple, splittable command (like a stray INSERT/GRANT), keep it whole.
        if is_complex_block and not any(cleaned_block_upper.startswith(cmd) for cmd in SPLITTABLE_COMMANDS):
            sanitized_statements.append(cleaned_block)
        
        else:
            # 4. Simple SQL/DDL (e.g., multiple GRANTs, multiple simple INSERTs).
            # These must be split by semicolon.
            
            # We ONLY use sqlparse.split if it's a SIMPLE statement OR contains multiple semicolons.
            if cleaned_block.count(';') > 0:
                inner_statements = sqlparse.split(cleaned_block)

                for stmt in inner_statements:
                    final_stmt = stmt.strip()
                    if final_stmt:
                        sanitized_statements.append(final_stmt)
            else:
                 # A single, simple statement without a semicolon
                sanitized_statements.append(cleaned_block)
                    
    return sanitized_statements



