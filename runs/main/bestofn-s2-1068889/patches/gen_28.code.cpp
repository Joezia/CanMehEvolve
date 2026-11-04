
FIT_UINT8 Field::GetNum(void) const
{
    // Early exit for NULL profile avoids bounds check overhead
    if (profile == NULL) return FIT_FIELD_NUM_INVALID;
    // Inline bounds check with direct access after validation
    return (profileIndex < profile->numFields) ? profile->fields[profileIndex].num : FIT_FIELD_NUM_INVALID;
}
