
FIT_UINT8 Field::GetType() const
{
    if (type != FIT_UINT8_INVALID)
        return type;

    if (!profile || profileIndex >= profile->numFields)
        return FIT_UINT8_INVALID;

    // Inline the lookup to avoid potential bounds check overhead and enable better optimization
    return profile->fields[profileIndex].type;
}
