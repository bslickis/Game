####################
# Define variables
####################
# General parameters
windowSizeX = 700  # Vertical size of the window
windowSizeY = 500  # Horizontal size of the window
startPointX = -250  # X coordinate to begin drawing
startPointY = -165  # Y coordinate to begin drawing
colorOutline = "black"  # Color for outlines
colorBackground = "black"  # Color for the background
drawingSpeed = 0  # Speed the cursor moves (1 is slow, 10 is fast)

# Stripe parameters
stripeWidth = 500  # How long the stripes should be in pixels
stripeHeight = 30  # How tall the stripes should be in pixels
stripeAngle = 90  # How many degrees to turn when drawing stripe edges
stripeColorOdd = "red"  # Odd numbered stripes should be red
stripeColorEven = "white"  # Even numbered stripes should be white

# Square parameters
squareWidth = stripeWidth * 0.4  # The square covers 40% of the width
squareHeight = stripeHeight * 7  # The square covers seven stripes
squareAngle = 90  # How many degrees to turn when drawing the blue square
squareColor = "blue"  # Color for the background of the square

# Star parameters
starLength = 8  # Length of the star lines
starAngle = 144  # The angle to turn when drawing the star
starSpacerX = 30
starSpacerY = 20
starOffset = starSpacerX / 2
starColor = "white"  # Color for the stars

####################
# Create objects
####################
# Import the turtle library to create a window and set its parameters
import turtle  # Create the window/canvas
turtle.bgcolor(colorBackground)  # Set the background color
turtle.setup(windowSizeX, windowSizeY)  # Adjust the window size

# Create a turtle object called t
t = turtle.Turtle()  # This will be the cursor we draw with
t.speed(drawingSpeed)  # Set the cursor speed
t.pencolor(colorOutline)  # Set the pen color to draw outlines

####################
# Define functions
####################
def DrawSquare(squareFillColor):
    t.fillcolor(squareFillColor)  # Set the fill color for the square
    t.begin_fill()  # Turn on fill so the square is colored in

    # Draw the outline of the stripe
    for thisHalf in range(2):  # Repeat twice for each half of the square outline
        t.fd(squareWidth)  # Draw a horizontal line
        t.rt(squareAngle)  # Turn to the right
        t.fd(squareHeight)  # Drw a vertical line
        t.rt(squareAngle)  # Turn to the right

    t.end_fill()  # Turn off fill after the square is drawn and filled

def DrawStripe(stripeFillColor):
    t.fillcolor(stripeFillColor)  # Set the fill color for this stripe
    t.begin_fill()  # Turn on fill so the stripe is colored in

    # Draw the outline of the stripe
    for thisHalf in range(2):  # Repeat twice for each half of the stripe outline
        t.fd(stripeWidth)  # Draw a horizontal line
        t.rt(stripeAngle)  # Turn to the right
        t.fd(stripeHeight)  # Draw a vertical line
        t.rt(stripeAngle)  # Turn to the right

    t.end_fill()  # Turn off fill after the stripe is drawn and filled

def DrawStar(starFillColor):
    t.fillcolor(starFillColor)  # Set the fill color for this stripe
    t.begin_fill()  # Turn on fill so the stripe is colored in

    for side in range(5):
        t.fd(starLength)  # Draw a line
        t.rt(starAngle)  # Rotate at the peak of the star
        t.fd(starLength)  # Draw the next line
        t.rt(72 - starAngle)  # Rotate at the trough of the star

    t.end_fill()  # Turn off fill after the stripe is colored in

def MoveCursor(X, Y):
    t.penup()  # Pick up the pen to stop drawing
    t.goto(X, Y)  # Move to the specified coordinates
    t.pendown()  # Put down the pen to start drawing

####################
# Draw the flag
####################
# Move to the starting position
MoveCursor(startPointX, startPointY)

for thisStripe in range(13):  # Loop to draw 13 stripes of alternating color
    if thisStripe % 2:  # Determine if this is an even or odd numbered line
        DrawStripe(stripeColorEven)  # Draw an even-numbered stripe
    else:
        DrawStripe(stripeColorOdd)  # Draw an odd-numbered stripe

    # Go to the vertical point to start drawing the next stripe by moving up one stripeHeight
    # for each stripe drawn so far. Add +1 to thisStripe to account for the zero-based index
    if thisStripe < 12:  # Don't move up if we just drew the last stripe
        MoveCursor(t.xcor(), startPointY + (stripeHeight * (thisStripe+1)))

DrawSquare(squareColor)  # Add the box over the upper-left stripes

# Draw the stars
MoveCursor(t.xcor() - 5, t.ycor() - starSpacerY)  # Get in position to start drawing stars
for thisRow in range(9):  # Draw nine rows of stars
    if thisRow % 2:  # This is an odd row
        MoveCursor(t.xcor() + (starOffset), t.ycor())  # Indent for odd rows
        for thisStar in range(5):  # Draw five stars on odd rows
            MoveCursor(t.xcor() + (starSpacerX), t.ycor())  # Move the cursor to draw the next star
            DrawStar(starColor)  # Draw a star
        MoveCursor(t.xcor() - (starSpacerX * 5) - starOffset, t.ycor() - starSpacerY)  # Move the cursor down and back
    else:  # This is an even row
        for thisStar in range(6):  # Draw six stars on even rows
            MoveCursor(t.xcor() + starSpacerX, t.ycor())  # Move the cursor to draw the next star
            DrawStar(starColor)  # Draw a star
        MoveCursor(t.xcor() - (starSpacerX * 6), t.ycor() - starSpacerY)  # Move the cursor down and back


turtle.exitonclick() # Close the turtle canvas when clicked
