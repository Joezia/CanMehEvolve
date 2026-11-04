FIT_UINT8 Field::GetType() const
{
    if ((type == FIT_UINT8_INVALID) &&
        (profile != NULL) &&
        (profileIndex < profile->numFields))
    {
        return profile->fields[profileIndex].type;
    }

    return type;
}
