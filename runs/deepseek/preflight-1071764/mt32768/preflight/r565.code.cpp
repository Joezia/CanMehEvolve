FIT_BOOL MesgDefinition::Supports(const MesgDefinition& mesgDef) const
{
    if (num != mesgDef.num)
        return FIT_FALSE;

    if (localNum != mesgDef.localNum)
        return FIT_FALSE;

    const size_t fieldCount = mesgDef.fields.size();
    const size_t supportedFieldCount = fields.size();
    unsigned long long seen[4] = {0, 0, 0, 0};

    for (size_t i = 0; i < fieldCount; ++i)
    {
        const FieldDefinition& mesgField = mesgDef.fields[i];
        const FIT_UINT8 mesgFieldNum = mesgField.GetNum();
        const FieldDefinition* supportedFieldDef = FIT_NULL;

        if (i < supportedFieldCount)
        {
            const FieldDefinition& supportedField = fields[i];
            const FIT_UINT8 supportedNum = supportedField.GetNum();

            if (supportedNum == mesgFieldNum &&
                (seen[supportedNum >> 6] & (1ULL << (supportedNum & 63))) == 0)
            {
                supportedFieldDef = &supportedField;
            }

            seen[supportedNum >> 6] |= (1ULL << (supportedNum & 63));
        }

        if (supportedFieldDef == FIT_NULL)
        {
            supportedFieldDef = GetField(mesgFieldNum);
            if (supportedFieldDef == FIT_NULL)
                return FIT_FALSE;
        }

        if (mesgField.GetSize() > supportedFieldDef->GetSize())
            return FIT_FALSE;
    }

    const size_t devFieldCount = mesgDef.devFields.size();
    for (size_t i = 0; i < devFieldCount; ++i)
    {
        const DeveloperFieldDefinition& fieldDef = mesgDef.devFields[i];
        const DeveloperFieldDefinition* supportedDef =
            GetDevField(fieldDef.GetDeveloperDataIndex(), fieldDef.GetNum());

        if (supportedDef == FIT_NULL)
            return FIT_FALSE;

        if (fieldDef.GetSize() > supportedDef->GetSize())
            return FIT_FALSE;
    }

    return FIT_TRUE;
}
