FIT_UINT8 Field::GetType() const
{
    if (type != FIT_UINT8_INVALID)
        return type;

    if (profile == NULL || profileIndex >= profile->numFields)
        return FIT_UINT8_INVALID;

    return profile->fields[profileIndex].type;
}
