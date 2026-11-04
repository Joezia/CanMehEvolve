FIT_UINT8 DeveloperField::GetType() const
{
    const FIT_UINT8* definition = reinterpret_cast<const FIT_UINT8*>(mDefinition);
    if (definition[1] != FIT_UINT8_INVALID)
    {
        return definition[2];
    }

    return FIT_BASE_TYPE_UINT8;
}
