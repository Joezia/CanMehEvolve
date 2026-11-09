
FIT_BOOL Decode::Resume(void)
{
    pause = FIT_FALSE;
    RETURN decodeReturn = RETURN_CONTINUE;

    do
    {
        if (currentByteIndex == 0)
        {
            file->read(buffer, BufferSize);
            bytesRead = static_cast<FIT_UINT32>(file->gcount());
        }

        for (; currentByteIndex < bytesRead; currentByteIndex++)
        {
            if (pause)
                return FIT_FALSE;

            decodeReturn = ReadByte(static_cast<FIT_UINT8>(buffer[currentByteIndex]));

            switch (decodeReturn)
            {
                case RETURN_CONTINUE:
                    break;

                case RETURN_MESG:
                {
                    const FIT_UINT8 num = mesg.GetNum();
                    if (num == FIT_MESG_NUM_DEVELOPER_DATA_ID)
                    {
                        DeveloperDataIdMesg devIdMesg(mesg);

                        if (!devIdMesg.IsDeveloperDataIndexValid())
                            throw fit::RuntimeException("Invalid developer data index in DeveloperDataIdMesg");

                        const FIT_UINT8 index = devIdMesg.GetDeveloperDataIndex();
                        developers[index] = std::move(devIdMesg);
                        descriptions[index].clear(); // Reuse existing map, avoid reallocation
                    }
                    else if (num == FIT_MESG_NUM_FIELD_DESCRIPTION)
                    {
                        FieldDescriptionMesg descMesg(mesg);

                        if (!descMesg.IsDeveloperDataIndexValid() || !descMesg.IsFieldDefinitionNumberValid())
                            throw fit::RuntimeException("Invalid developer field definition in FieldDescriptionMesg");

                        const FIT_UINT8 index = descMesg.GetDeveloperDataIndex();
                        const FIT_UINT8 fldNum = descMesg.GetFieldDefinitionNumber();

                        try
                        {
                            descriptions[index][fldNum] = std::move(descMesg);

                            if (descriptionListener)
                                descriptionListener->OnDeveloperFieldDescription(DeveloperFieldDescription(descriptions[index][fldNum], developers[index]));
                        }
                        catch (const std::out_of_range&)
                        {
                            // Description without Developer Data Id Message
                        }
                    }

                    if (mesgListener)
                        mesgListener->OnMesg(mesg);
                    break;
                }

                case RETURN_MESG_DEF:
                    if (mesgDefinitionListener)
                        mesgDefinitionListener->OnMesgDefinition(localMesgDefs[localMesgIndex]);
                    break;

                case RETURN_END_OF_FILE:
                    currentByteIndex++;
                    currentByteOffset++;
                    return FIT_TRUE;

                default:
                    currentByteOffset++;
                    return FIT_TRUE;
            }
            currentByteOffset++;
        }
        currentByteIndex = 0;
    } while (file->good());

    if ((streamIsComplete == FIT_TRUE) && (skipHeader == FIT_FALSE))
    {
        std::ostringstream message;
        message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
        throw RuntimeException(message.str());
    }

    if (streamIsComplete == FIT_FALSE)
    {
        if ((decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF))
            return FIT_TRUE;
        return FIT_FALSE;
    }

    if ((decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF))
        return FIT_TRUE;

    if (invalidDataSize == FIT_FALSE)
    {
        std::ostringstream message;
        message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
        throw RuntimeException(message.str());
    }

    return FIT_TRUE;
}
