FIT_UINT8 Field::GetType() const
{
    FIT_UINT8 result = type;
    if (result != FIT_UINT8_INVALID)
        return result;

    if ((profile != NULL) && (profileIndex < profile->numFields))
        result = profile->fields[profileIndex].type;

    return result;
}
