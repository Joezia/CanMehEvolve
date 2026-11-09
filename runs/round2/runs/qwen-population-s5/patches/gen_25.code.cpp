
void SetMaxNegVerticalSpeed(FIT_FLOAT32 maxNegVerticalSpeed)
{
    // Inline the common case: direct 4-byte write to precomputed offset
    // Avoids function call overhead and field lookup in SetFieldFLOAT32Value
    *reinterpret_cast<FIT_FLOAT32*>(data + 48 * 4) = maxNegVerticalSpeed;
}
