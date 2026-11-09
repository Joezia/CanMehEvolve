FIT_BOOL Decode::Resume(void)
{
    pause = FIT_FALSE;
    RETURN decodeReturn = RETURN_CONTINUE;

    bool paused = false;

    do
    {
        if ( currentByteIndex == 0 )
        {
            file->read(buffer, BufferSize);
            bytesRead = (FIT_UINT32)file->gcount();

            if ( paused )
            {
                if ( bytesRead > 0 )
                {
                    currentByteIndex = 0;
                    return FIT_FALSE;
                }
                paused = false;
            }
        }

        FIT_UINT32 index = currentByteIndex;
        FIT_UINT32 offset = currentByteOffset;
        const FIT_UINT32 count = bytesRead;
        const FIT_UINT8* p = buffer + index;
        const FIT_UINT8* const end = buffer + count;

        for ( ; p < end; ++p, ++index )
        {
            decodeReturn = ReadByte(*p);

            if ( __builtin_expect(decodeReturn == RETURN_CONTINUE, 1) )
            {
                ++offset;
                continue;
            }

            if ( decodeReturn == RETURN_MESG )
            {
                currentByteIndex = index;
                currentByteOffset = offset;

                const auto mesgNum = mesg.GetNum();
                if ( mesgNum == FIT_MESG_NUM_DEVELOPER_DATA_ID )
                {
                    DeveloperDataIdMesg devIdMesg(mesg);

                    if ( !devIdMesg.IsDeveloperDataIndexValid() )
                    {
                        throw fit::RuntimeException("Invalid developer data index in DeveloperDataIdMesg");
                    }

                    FIT_UINT8 devIndex = devIdMesg.GetDeveloperDataIndex();
                    developers[devIndex] = devIdMesg;
                    descriptions[devIndex] = std::unordered_map<FIT_UINT8, FieldDescriptionMesg>();
                }
                else if ( mesgNum == FIT_MESG_NUM_FIELD_DESCRIPTION )
                {
                    FieldDescriptionMesg descMesg(mesg);

                    if ( !descMesg.IsDeveloperDataIndexValid() )
                    {
                        throw fit::RuntimeException("Invalid developer data index in FieldDescriptionMesg");
                    }

                    if ( !descMesg.IsFieldDefinitionNumberValid() )
                    {
                        throw fit::RuntimeException("Invalid developer field definition number in FieldDescriptionMesg");
                    }

                    FIT_UINT8 devIndex = descMesg.GetDeveloperDataIndex();
                    FIT_UINT8 fldNum = descMesg.GetFieldDefinitionNumber();

                    auto descIt = descriptions.find(devIndex);
                    if ( descIt != descriptions.end() )
                    {
                        descIt->second[fldNum] = descMesg;

                        if ( descriptionListener )
                        {
                            descriptionListener->OnDeveloperFieldDescription(DeveloperFieldDescription(descMesg, developers[devIndex]));
                        }
                    }
                }

                if ( mesgListener )
                {
                    mesgListener->OnMesg(mesg);
                }

                ++offset;

                if ( __builtin_expect(pause, 0) )
                {
                    if ( index + 1 < count )
                    {
                        currentByteIndex = index + 1;
                        currentByteOffset = offset;
                        return FIT_FALSE;
                    }
                    paused = true;
                }
                continue;
            }

            if ( decodeReturn == RETURN_MESG_DEF )
            {
                currentByteIndex = index;
                currentByteOffset = offset;

                if ( mesgDefinitionListener )
                {
                    mesgDefinitionListener->OnMesgDefinition(localMesgDefs[localMesgIndex]);
                }

                ++offset;

                if ( __builtin_expect(pause, 0) )
                {
                    if ( index + 1 < count )
                    {
                        currentByteIndex = index + 1;
                        currentByteOffset = offset;
                        return FIT_FALSE;
                    }
                    paused = true;
                }
                continue;
            }

            if ( decodeReturn == RETURN_END_OF_FILE )
            {
                currentByteIndex = index + 1;
                currentByteOffset = offset + 1;
                return FIT_TRUE;
            }

            currentByteIndex = index;
            currentByteOffset = offset + 1;
            return FIT_TRUE;
        }

        currentByteIndex = 0;
        currentByteOffset = offset;
    } while ( file->good() );

    if ( (streamIsComplete == FIT_TRUE) && (skipHeader == FIT_FALSE) )
    {
        std::ostringstream message;
        message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
        throw RuntimeException(message.str());
    }
    if ( streamIsComplete == FIT_FALSE )
    {
        if ( (decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF) )
        {
            return FIT_TRUE;
        }
        else
        {
            return FIT_FALSE;
        }
    }
    else
    {
        if ( (decodeReturn == RETURN_MESG) || (decodeReturn == RETURN_MESG_DEF) )
        {
            return FIT_TRUE;
        }
        else
        {
            if ( invalidDataSize == FIT_FALSE )
            {
                std::ostringstream message;
                message << "FIT decode error: Unexpected end of input stream at byte: " << currentByteOffset;
                throw RuntimeException(message.str());
            }
            else
            {
                return FIT_TRUE;
            }
        }
    }
}
